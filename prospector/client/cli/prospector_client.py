import sys
from datetime import datetime
from pprint import pprint

import requests
from tqdm import tqdm

from commit_processor.feature_extractor import extract_features
from commit_processor.preprocessor import preprocess_commit
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from filter_rank.rank import rank
from filter_rank.rules import apply_rules
from git.git import GIT_CACHE
from git.git import Commit as GitCommit
from git.git import Git

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
    modified_files: "list[str]" = [],
    time_limit_before: int = TIME_LIMIT_BEFORE,
    time_limit_after: int = TIME_LIMIT_AFTER,
    use_nvd: bool = False,
    nvd_rest_endpoint: str = "",
    git_cache: str = GIT_CACHE,
    verbose: bool = False,
    debug: bool = True,
    limit_candidates: int = MAX_CANDIDATES,
    handcrafted_rules: "list[str]" = ["ALL"],
    model_name: str = "",
) -> "list[Commit]":

    if debug:
        verbose = True

    advisory_record = AdvisoryRecord(
        vulnerability_id=vulnerability_id,
        repository_url=repository_url,
        description=vuln_descr,
        from_nvd=use_nvd,
        nvd_rest_endpoint=nvd_rest_endpoint,
    )

    if debug:
        pprint(advisory_record)

    advisory_record.analyze(use_nvd=use_nvd)
    print(advisory_record.code_tokens)

    if publication_date != "":
        advisory_record.published_timestamp = int(
            datetime.strptime(publication_date, r"%Y-%m-%dT%H:%M%z").timestamp()
        )

    # print(advisory_record.paths)

    print("Downloading repository {} in {}..".format(repository_url, git_cache))
    repository = Git(repository_url, git_cache)
    repository.clone()
    tags = repository.get_tags()

    if debug:
        print("Found tags:")
        print(tags)

    print("Done retrieving %s" % repository_url)

    prev_tag = None
    following_tag = None
    if tag_interval != "":
        prev_tag, following_tag = tag_interval.split(":")

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

    print("found %d candidates" % len(candidates))
    # if some code_tokens were found in the advisory text, require
    # that candidate commits touch some file whose path contains those tokens
    # NOTE: this works quite well for Java, not sure how general this criterion is

    if advisory_record.code_tokens != []:
        print(
            "Detected tokens in advisory text, searching for files whose path contains those tokens"
        )
        print(advisory_record.code_tokens)

    if modified_files == [""]:
        modified_files = advisory_record.code_tokens
    else:
        modified_files.extend(advisory_record.code_tokens)

    candidates = filter_by_changed_files(candidates, modified_files, repository)

    # end of filtering

    if debug:
        print("Collected %d candidates" % len(candidates))

    if len(candidates) > limit_candidates:
        print("Number of candidates exceeds %d, aborting." % limit_candidates)
        sys.exit(-1)

    preprocessed_commits: "list[GitCommit]" = []
    pbar = tqdm(candidates)
    for commit_id in pbar:
        preprocessed_commits.append(preprocess_commit(repository.get_commit(commit_id)))

    commit_with_features = []
    for datamodel_commit in tqdm(preprocessed_commits):
        commit_with_features.append(extract_features(datamodel_commit, advisory_record))

    rule_application_result = apply_rules(commit_with_features, rules=handcrafted_rules)

    if debug:
        pprint(advisory_record)

    if verbose:
        print("preprocessed %d commits" % len(preprocessed_commits))

    payload = [c.__dict__ for c in preprocessed_commits]

    # TODO read backend address from config file
    try:
        r = requests.post("http://localhost:8000/commits/", json=payload)
        print("Status: %d" % r.status_code)
    except requests.exceptions.ConnectionError:
        print("Could not reach backend, is it running?")
        print("The result of commit pre-processing will not be saved.")

    # TODO compute actual rank
    # This is done by a POST request that creates a "search" job
    # whose inputs are the AdvisoryRecord, and the repository URL
    # The API returns immediately indicating a job id. From this
    # id, a URL can be constructed to poll the results asynchronously.
    ranked_results = [repository.get_commit(c) for c in preprocessed_commits]

    ranked_results = rank(commit_with_features, model_name=model_name)

    return rule_application_result, ranked_results


def filter_by_changed_files(
    candidates: "list[str]", modified_files: "list[str]", git_repository: Git
) -> list:
    """
    Takes a list of commit ids in input and returns in output the list
    of ids of the commits that modify at least one path that contains one of the strings
    in "modified_files"

    """
    modified_files = [f.lower() for f in modified_files if f != ""]
    if len(modified_files) == 0:
        return candidates

    filtered_candidates = []
    if len(modified_files) != 0:
        for commit_id in candidates:
            commit_obj = git_repository.get_commit(commit_id)
            commit_changed_files = commit_obj.get_changed_files()
            for ccf in commit_changed_files:
                for f in modified_files:
                    ccf = ccf.lower()
                    if f in ccf:
                        # if f in [e.lower() for e in ccf]:
                        # print(f, commit_obj.get_id())
                        filtered_candidates.append(commit_obj.get_id())

    return list(set(filtered_candidates))
