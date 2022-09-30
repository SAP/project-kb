import logging
import sys
from datetime import datetime
from typing import List, Tuple

import requests
from tqdm import tqdm

import log
from client.cli.console import ConsoleWriter, MessageStatus
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit, apply_ranking, make_from_raw_commit
from filtering.filter import filter_commits
from git.git import GIT_CACHE, Git
from git.version_to_tag import get_tag_for_version
from log.util import init_local_logger
from rules import apply_rules

# from util.profile import profile
from stats.execution import (
    Counter,
    ExecutionTimer,
    execution_statistics,
    measure_execution_time,
)

_logger = init_local_logger()

SECS_PER_DAY = 86400
TIME_LIMIT_BEFORE = 3 * 365 * SECS_PER_DAY
TIME_LIMIT_AFTER = 180 * SECS_PER_DAY

MAX_CANDIDATES = 1000

core_statistics = execution_statistics.sub_collection("core")


# @profile
@measure_execution_time(execution_statistics, name="core")
def prospector(  # noqa: C901
    vulnerability_id: str,
    repository_url: str,
    publication_date: str = "",
    vuln_descr: str = "",
    tag_interval: str = "",
    filter_extensions: str = "",
    version_interval: str = "",
    modified_files: "list[str]" = [],
    advisory_keywords: "list[str]" = [],
    time_limit_before: int = TIME_LIMIT_BEFORE,
    time_limit_after: int = TIME_LIMIT_AFTER,
    use_nvd: bool = True,
    nvd_rest_endpoint: str = "",
    fetch_references: bool = False,
    backend_address: str = "",
    git_cache: str = GIT_CACHE,
    limit_candidates: int = MAX_CANDIDATES,
    rules: "list[str]" = ["ALL"],
) -> Tuple[List[Commit], AdvisoryRecord]:

    _logger.debug("begin main commit and CVE processing")

    # construct an advisory record
    with ConsoleWriter("Processing advisory"):
        advisory_record = build_advisory_record(
            vulnerability_id,
            repository_url,
            vuln_descr,
            nvd_rest_endpoint,
            fetch_references,
            use_nvd,
            publication_date,
            advisory_keywords,
            modified_files,
        )

    with ConsoleWriter("Obtaining initial set of candidates") as writer:

        # obtain a repository object
        repository = Git(repository_url, git_cache)

        # retrieve of commit candidates
        candidates = get_candidates(
            advisory_record,
            repository,
            tag_interval,
            version_interval,
            time_limit_before,
            time_limit_after,
            filter_extensions,
        )
        _logger.debug(f"Collected {len(candidates)} candidates")

        if len(candidates) > limit_candidates:
            _logger.error(
                "Number of candidates exceeds %d, aborting." % limit_candidates
            )
            _logger.error(
                "Possible cause: the backend might be unreachable or otherwise unable to provide details about the advisory."
            )
            writer.print(
                f"Found {len(candidates)} candidates, too many to proceed.",
                status=MessageStatus.ERROR,
            )
            writer.print("Please try running the tool again.")
            sys.exit(-1)

        writer.print(f"Found {len(candidates)} candidates")

    # -------------------------------------------------------------------------
    # commit preprocessing
    # -------------------------------------------------------------------------
    with ExecutionTimer(
        core_statistics.sub_collection(name="commit preprocessing")
    ) as timer:
        with ConsoleWriter("Preprocessing commits") as writer:
            retrieved_commits = dict()
            missing = []
            try:
                # Use the preprocessed commits already stored in the backend
                # and only process those that are missing.
                r = requests.get(
                    f"{backend_address}/commits/{repository_url}?commit_id={','.join(candidates)}"
                )

                _logger.debug(f"The backend returned status {r.status_code}")
                if r.status_code != 200:
                    _logger.info("Preprocessed commits not found in the backend")
                    missing = candidates
                else:
                    retrieved_commits = r.json()
                    _logger.info(f"Found {len(retrieved_commits)} preprocessed commits")
                    if len(retrieved_commits) != len(candidates):
                        missing = list(
                            set(candidates).difference(
                                rc["commit_id"] for rc in retrieved_commits
                            )
                        )
                        _logger.error(f"Missing {len(missing)} commits")

            except requests.exceptions.ConnectionError:
                print(
                    "Could not reach backend, is it running? The result of commit pre-processing will not be saved. (Check the logs for details)"
                )
                _logger.error(
                    "Could not reach backend, is it running? The result of commit pre-processing will not be saved.",
                    exc_info=log.config.level < logging.WARNING,
                )
                missing = candidates

            preprocessed_commits: "list[Commit]" = []
            for idx, commit in enumerate(retrieved_commits):
                if len(retrieved_commits) + len(missing) == len(
                    candidates
                ):  # None results are not in the DB, collect them to missing list, they need local preprocessing
                    preprocessed_commits.append(
                        Commit.parse_obj(commit)
                    )  # TODO: Verify this parsing
                else:
                    missing.append(candidates[idx])

            # first_missing = len(preprocessed_commits)
            pbar = tqdm(missing, desc="Preprocessing commits", unit="commit")
            with Counter(
                timer.collection.sub_collection(name="commit preprocessing")
            ) as counter:
                counter.initialize("preprocessed commits", unit="commit")
                for commit_id in pbar:
                    counter.increment("preprocessed commits")
                    preprocessed_commits.append(
                        make_from_raw_commit(repository.get_commit(commit_id))
                    )

            _logger.pretty_log(advisory_record)
            _logger.debug(f"preprocessed {len(preprocessed_commits)} commits")

            payload = [c.__dict__ for c in preprocessed_commits]

    # -------------------------------------------------------------------------
    # save preprocessed commits to backend
    # -------------------------------------------------------------------------
    if len(payload) > 0 and len(missing) > 0:
        with ExecutionTimer(
            core_statistics.sub_collection(name="save preprocessed commits to backend")
        ):
            with ConsoleWriter("Saving preprocessed commits to backend") as writer:
                _logger.debug("Sending preprocessing commits to backend...")
                try:
                    r = requests.post(backend_address + "/commits/", json=payload)
                    _logger.debug(
                        "Saving to backend completed (status code: %d)" % r.status_code
                    )
                except requests.exceptions.ConnectionError:
                    _logger.error(
                        "Could not reach backend, is it running?"
                        "The result of commit pre-processing will not be saved."
                        "Continuing anyway.....",
                        exc_info=log.config.level < logging.WARNING,
                    )
                    writer.print(
                        "Could not save preprocessed commits to backend",
                        status=MessageStatus.WARNING,
                    )
    else:
        _logger.warning("No preprocessed commits to send to backend.")

    # -------------------------------------------------------------------------
    # analyze candidates by applying rules
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # filter commits
    #
    # Here we apply additional criteria to discard commits from the initial
    # set extracted from the repository
    # -------------------------------------------------------------------------
    with ConsoleWriter("Candidate filtering") as console:
        candidate_count = len(preprocessed_commits)
        console.print(f"Filtering {candidate_count} candidates")

        preprocessed_commits, rejected = filter_commits(preprocessed_commits)
        if len(rejected) > 0:
            console.print(f"Dropped {len(rejected)} candidates")
            # Maybe print reasons for rejection?
            # console.print(f"{rejected}")

    with ExecutionTimer(
        core_statistics.sub_collection(name="analyze candidates")
    ) as timer:
        with ConsoleWriter("Applying rules"):
            annotated_candidates = apply_rules(
                preprocessed_commits, advisory_record, rules=rules
            )

            annotated_candidates = apply_ranking(annotated_candidates)

    return annotated_candidates, advisory_record


def build_advisory_record(
    vulnerability_id,
    repository_url,
    vuln_descr,
    nvd_rest_endpoint,
    fetch_references,
    use_nvd,
    publication_date,
    advisory_keywords,
    modified_files,
) -> AdvisoryRecord:

    advisory_record = AdvisoryRecord(
        vulnerability_id=vulnerability_id,
        repository_url=repository_url,
        description=vuln_descr,
        from_nvd=use_nvd,
        nvd_rest_endpoint=nvd_rest_endpoint,
    )

    _logger.pretty_log(advisory_record)

    advisory_record.analyze(use_nvd=use_nvd, fetch_references=fetch_references)
    _logger.debug(f"{advisory_record.keywords=}")

    if publication_date != "":
        advisory_record.published_timestamp = int(
            datetime.strptime(publication_date, r"%Y-%m-%dT%H:%M%z").timestamp()
        )

    if len(advisory_keywords) > 0:
        advisory_record.keywords += tuple(advisory_keywords)
        # drop duplicates
        advisory_record.keywords = list(set(advisory_record.keywords))

    # FIXME this should be handled better (or '' should not end up in the modified_files in
    # the first place)
    if modified_files != [""]:
        advisory_record.paths += modified_files

    _logger.debug(f"{advisory_record.keywords=}")
    _logger.debug(f"{advisory_record.paths=}")

    return advisory_record


def get_candidates(
    advisory_record,
    repository,
    tag_interval,
    version_interval,
    time_limit_before,
    time_limit_after,
    filter_extensions,
) -> List[str]:
    with ExecutionTimer(
        core_statistics.sub_collection(name="retrieval of commit candidates")
    ):
        with ConsoleWriter("Git repository cloning"):
            _logger.info(
                f"Downloading repository {repository._url} in {repository._path}"
            )
            repository.clone()

            tags = repository.get_tags()

            _logger.debug(f"Found tags: {tags}")
            _logger.info(f"Done retrieving {repository._url}")

        with ConsoleWriter("Candidate commit retrieval"):
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
                filter_files=filter_extensions,
            )

            core_statistics.record("candidates", len(candidates), unit="commits")
            _logger.info("Found %d candidates" % len(candidates))

    return candidates
