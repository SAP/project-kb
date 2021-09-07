import logging
import sys
from datetime import datetime

import requests
from tqdm import tqdm

import log
from commit_processor.feature_extractor import extract_features
from commit_processor.preprocessor import preprocess_commit
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from filter_rank.filter import filter_commits
from filter_rank.rank import rank
from filter_rank.rules import apply_rules
from git.git import GIT_CACHE, Git
from git.version_to_tag import get_tag_for_version
from log.util import init_local_logger

_logger = init_local_logger()

SECS_PER_DAY = 86400
TIME_LIMIT_BEFORE = 3 * 365 * SECS_PER_DAY
TIME_LIMIT_AFTER = 180 * SECS_PER_DAY

MAX_CANDIDATES = 1000


def prospector(  # noqa: C901
    vulnerability_id: str,
    repository_url: str,
    publication_date: str = "",
    vuln_descr: str = "",
    tag_interval: str = "",
    version_interval: str = "",
    modified_files: "list[str]" = [],
    code_tokens: "list[str]" = [],
    time_limit_before: int = TIME_LIMIT_BEFORE,
    time_limit_after: int = TIME_LIMIT_AFTER,
    use_nvd: bool = False,
    nvd_rest_endpoint: str = "",
    backend_address: str = "",
    git_cache: str = GIT_CACHE,
    limit_candidates: int = MAX_CANDIDATES,
    active_rules: "list[str]" = ["ALL"],
    model_name: str = "",
) -> "list[Commit]":

    _logger.info("begin main commit and CVE processing")

    # -------------------------------------------------------------------------
    # advisory record extraction
    # -------------------------------------------------------------------------
    advisory_record = AdvisoryRecord(
        vulnerability_id=vulnerability_id,
        repository_url=repository_url,
        description=vuln_descr,
        from_nvd=use_nvd,
        nvd_rest_endpoint=nvd_rest_endpoint,
    )

    _logger.pretty_log(advisory_record)

    advisory_record.analyze(use_nvd=use_nvd)

    if publication_date != "":
        advisory_record.published_timestamp = int(
            datetime.strptime(publication_date, r"%Y-%m-%dT%H:%M%z").timestamp()
        )

    if len(code_tokens) > 0:
        advisory_record.code_tokens += code_tokens

    # FIXME this should be handled better (or '' should not end up in the modified_files in
    # the first place)
    if modified_files != [""]:
        advisory_record.paths += modified_files

    _logger.info(f"{advisory_record.code_tokens=}")
    # print(advisory_record.paths)

    # -------------------------------------------------------------------------
    # retrieval of commit candidates
    # -------------------------------------------------------------------------
    _logger.info("Downloading repository {} in {}..".format(repository_url, git_cache))
    repository = Git(repository_url, git_cache)
    repository.clone()
    tags = repository.get_tags()

    _logger.debug(f"Found tags: {tags}")

    _logger.info("Done retrieving %s" % repository_url)

    prev_tag = None
    following_tag = None
    if tag_interval != "":
        prev_tag, following_tag = tag_interval.split(":")
    elif version_interval != "":
        vuln_version, fixed_version = version_interval.split(":")
        prev_tag = get_tag_for_version(tags, vuln_version)[0]
        following_tag = get_tag_for_version(tags, fixed_version)[0]

    since = None
    until = None
    if advisory_record.published_timestamp:
        since = advisory_record.published_timestamp - time_limit_before
        until = advisory_record.published_timestamp + time_limit_after

    candidates = repository.get_commits(
        since=since,
        until=until,
        ancestors_of=following_tag,
        exclude_ancestors_of=prev_tag,
        filter_files="*.java",
    )

    _logger.info("Found %d candidates" % len(candidates))
    # if some code_tokens were found in the advisory text, require
    # that candidate commits touch some file whose path contains those tokens
    # NOTE: this works quite well for Java, not sure how general this criterion is

    # -------------------------------------------------------------------------
    # commit filtering
    #
    # Here we apply additional criteria to discard commits from the initial
    # set extracted from the repository
    # # -------------------------------------------------------------------------
    # if advisory_record.code_tokens != []:
    #     _logger.info(
    #         "Detected tokens in advisory text, searching for files whose path contains those tokens"
    #     )
    #     _logger.info(advisory_record.code_tokens)

    # if modified_files == [""]:
    #     modified_files = advisory_record.code_tokens
    # else:
    #     modified_files.extend(advisory_record.code_tokens)

    # candidates = filter_by_changed_files(candidates, modified_files, repository)

    candidates = filter_commits(candidates)

    _logger.debug(f"Collected {len(candidates)} candidates")

    if len(candidates) > limit_candidates:
        _logger.error("Number of candidates exceeds %d, aborting." % limit_candidates)
        _logger.error(
            "Possible cause: the backend might be unreachable or otherwise unable to provide details about the advisory."
        )
        sys.exit(-1)

    # -------------------------------------------------------------------------
    # commit preprocessing
    # -------------------------------------------------------------------------

    raw_commit_data = dict()
    missing = []
    try:
        # Exploit the preprocessed commits already stored in the backend
        #      and only process those that are missing. Note: the endpoint
        #      does not exist (yet)
        r = requests.get(
            backend_address
            + "/commits/"
            + repository_url
            + "?commit_id="
            + ",".join(candidates)
        )
        _logger.info("The backend returned status '%d'" % r.status_code)
        if r.status_code != 200:
            _logger.error("This is weird...Continuing anyway.")
            missing = candidates
        else:
            raw_commit_data = r.json()
            _logger.info("Found {} preprocessed commits".format(len(raw_commit_data)))
    except requests.exceptions.ConnectionError:
        _logger.error(
            "Could not reach backend, is it running? The result of commit pre-processing will not be saved.",
            exc_info=log.config.level < logging.WARNING,
        )
        missing = candidates

    preprocessed_commits: "list[Commit]" = []
    for idx, commit in enumerate(raw_commit_data):
        if (
            commit
        ):  # None results are not in the DB, collect them to missing list, they need local preprocessing
            preprocessed_commits.append(Commit.parse_obj(commit))
        else:
            missing.append(candidates[idx])

    _logger.info("Preprocessing commits...")
    first_missing = len(preprocessed_commits)
    pbar = tqdm(missing)
    for commit_id in pbar:
        preprocessed_commits.append(preprocess_commit(repository.get_commit(commit_id)))

    _logger.pretty_log(advisory_record)
    _logger.debug(f"preprocessed {len(preprocessed_commits)} commits")

    payload = [c.__dict__ for c in preprocessed_commits[first_missing:]]

    # -------------------------------------------------------------------------
    # save preprocessed commits to backend
    # -------------------------------------------------------------------------
    _logger.info("Sending preprocessing commits to backend...")
    try:
        r = requests.post(backend_address + "/commits/", json=payload)
        _logger.info("Saving to backend completed (status code: %d)" % r.status_code)
    except requests.exceptions.ConnectionError:
        _logger.error(
            "Could not reach backend, is it running?"
            "The result of commit pre-processing will not be saved."
            "Continuing anyway.....",
            exc_info=log.config.level < logging.WARNING,
        )

    # TODO compute actual rank
    # This can be done by a POST request that creates a "search" job
    # whose inputs are the AdvisoryRecord, and the repository URL
    # The API returns immediately indicating a job id. From this
    # id, a URL can be constructed to poll the results asynchronously.
    # ranked_results = [repository.get_commit(c) for c in preprocessed_commits]

    # -------------------------------------------------------------------------
    # analyze candidates by applying rules and ML predictor
    # -------------------------------------------------------------------------
    _logger.info("Extracting features from commits...")
    annotated_candidates = []
    for commit in tqdm(preprocessed_commits):
        annotated_candidates.append(extract_features(commit, advisory_record))

    annotated_candidates = apply_rules(
        annotated_candidates, advisory_record, active_rules=active_rules
    )
    annotated_candidates = rank(annotated_candidates, model_name=model_name)

    return annotated_candidates, advisory_record


# def filter_by_changed_files(
#     candidates: "list[str]", modified_files: "list[str]", git_repository: Git
# ) -> list:
#     """
#     Takes a list of commit ids in input and returns in output the list
#     of ids of the commits that modify at least one path that contains one of the strings
#     in "modified_files"

#     """
#     modified_files = [f.lower() for f in modified_files if f != ""]
#     if len(modified_files) == 0:
#         return candidates

#     filtered_candidates = []
#     if len(modified_files) != 0:
#         for commit_id in candidates:
#             commit_obj = git_repository.get_commit(commit_id)
#             commit_changed_files = commit_obj.get_changed_files()
#             for ccf in commit_changed_files:
#                 for f in modified_files:
#                     ccf = ccf.lower()
#                     if f in ccf:
#                         # if f in [e.lower() for e in ccf]:
#                         # print(f, commit_obj.get_id())
#                         filtered_candidates.append(commit_obj.get_id())

#     return list(set(filtered_candidates))
