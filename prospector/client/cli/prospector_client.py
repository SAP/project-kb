import logging
import sys
from datetime import datetime
from typing import List, Set, Tuple

import requests
from tqdm import tqdm

import log
from client.cli.console import ConsoleWriter, MessageStatus
from datamodel.advisory import AdvisoryRecord, build_advisory_record
from datamodel.commit import Commit, apply_ranking, make_from_dict, make_from_raw_commit
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
    filter_extensions: List[str] = [],
    version_interval: str = "",
    modified_files: Set[str] = set(),
    advisory_keywords: Set[str] = set(),
    time_limit_before: int = TIME_LIMIT_BEFORE,
    time_limit_after: int = TIME_LIMIT_AFTER,
    use_nvd: bool = True,
    nvd_rest_endpoint: str = "",
    fetch_references: bool = False,
    backend_address: str = "",
    use_backend: str = "always",
    git_cache: str = GIT_CACHE,
    limit_candidates: int = MAX_CANDIDATES,
    rules: List[str] = ["ALL"],
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
            filter_extensions,
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
            filter_extensions[0],
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
            try:
                if use_backend != "never":
                    missing, preprocessed_commits = retrieve_preprocessed_commits(
                        repository_url, backend_address, candidates
                    )
            except requests.exceptions.ConnectionError:
                print("Backend not reachable", end="")
                _logger.error(
                    "Backend not reachable",
                    exc_info=log.config.level < logging.WARNING,
                )
                if use_backend == "always":
                    print(": aborting")
                    sys.exit(0)
                print(": continuing without backend")
            finally:
                # If missing is not initialized and we are here, we initialize it
                if "missing" not in locals():
                    missing = candidates
                    preprocessed_commits = []

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
            payload = [c.as_dict() for c in preprocessed_commits]

    # -------------------------------------------------------------------------
    # save preprocessed commits to backend
    # -------------------------------------------------------------------------

    if (
        len(payload) > 0 and use_backend != "never"
    ):  # and len(missing) > 0:  # len(missing) is useless
        with ExecutionTimer(
            core_statistics.sub_collection(name="save preprocessed commits to backend")
        ):
            save_preprocessed_commits(backend_address, payload)
    else:
        _logger.warning("No preprocessed commits to send to backend.")

    # -------------------------------------------------------------------------
    # filter commits
    # -------------------------------------------------------------------------
    with ConsoleWriter("Candidate filtering") as console:
        candidate_count = len(preprocessed_commits)
        console.print(f"Filtering {candidate_count} candidates")

        preprocessed_commits, rejected = filter_commits(preprocessed_commits)
        if len(rejected) > 0:
            console.print(f"Dropped {len(rejected)} candidates")
            # Maybe print reasons for rejection? PUT THEM IN A FILE?
            # console.print(f"{rejected}")

    # -------------------------------------------------------------------------
    # analyze candidates by applying rules and rank them
    # -------------------------------------------------------------------------
    with ExecutionTimer(
        core_statistics.sub_collection(name="analyze candidates")
    ) as timer:
        with ConsoleWriter("Applying rules"):
            annotated_candidates = apply_rules(
                preprocessed_commits, advisory_record, rules=rules
            )

            annotated_candidates = apply_ranking(annotated_candidates)

    return annotated_candidates, advisory_record


def retrieve_preprocessed_commits(repository_url, backend_address, candidates):
    retrieved_commits = dict()
    missing = []

    # This will raise exception if backend is not reachable
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
                set(candidates).difference(rc["commit_id"] for rc in retrieved_commits)
            )
            _logger.error(f"Missing {len(missing)} commits")

    preprocessed_commits: "list[Commit]" = []
    for idx, commit in enumerate(retrieved_commits):
        if len(retrieved_commits) + len(missing) == len(candidates):
            preprocessed_commits.append(make_from_dict(commit))
        else:
            missing.append(candidates[idx])
    return missing, preprocessed_commits


def save_preprocessed_commits(backend_address, payload):
    with ConsoleWriter("Saving preprocessed commits to backend") as writer:
        _logger.debug("Sending preprocessing commits to backend...")
        try:
            r = requests.post(
                backend_address + "/commits/",
                json=payload,
                headers={"Content-type": "application/json"},
            )
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


# TODO: Cleanup many parameters should be recovered from the advisory record object
def get_candidates(
    advisory_record: AdvisoryRecord,
    repository: Git,
    tag_interval: str,
    version_interval: str,
    time_limit_before: int,
    time_limit_after: int,
    filter_extensions: str,
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
            # Here i need to strip the github tags of useless stuff
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
