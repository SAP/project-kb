import logging
import re
import sys
from typing import Dict, List, Set, Tuple

import requests
from tqdm import tqdm

from client.cli.console import ConsoleWriter, MessageStatus
from datamodel.advisory import AdvisoryRecord, build_advisory_record
from datamodel.commit import Commit, apply_ranking, make_from_raw_commit
from filtering.filter import filter_commits
from git.git import Git
from git.raw_commit import RawCommit
from git.version_to_tag import get_possible_tags
from log.logger import get_level, logger, pretty_log
from rules.rules import apply_rules
from stats.execution import (
    Counter,
    ExecutionTimer,
    execution_statistics,
    measure_execution_time,
)

SECS_PER_DAY = 86400
TIME_LIMIT_BEFORE = 3 * 365 * SECS_PER_DAY
TIME_LIMIT_AFTER = 180 * SECS_PER_DAY

MAX_CANDIDATES = 2000
DEFAULT_BACKEND = "http://localhost:8000"


core_statistics = execution_statistics.sub_collection("core")


def prospector_find_twins(
    vulnerability_id: str,
    repository_url: str,
    commit_id: str,
    git_cache: str = "/tmp/git_cache",
):
    advisory_record = build_advisory_record(
        vulnerability_id,
    )
    repository = Git(repository_url, git_cache)
    repository.clone()

    # tags = repository.get_tags()

    commits = repository.find_commits_for_twin_lookups(commit_id=commit_id)
    preprocessed_commits = list()
    pbar = tqdm(
        list(commits.values()),
        desc="Preprocessing commits",
        unit="commit",
    )
    for raw_commit in pbar:
        preprocessed_commits.append(make_from_raw_commit(raw_commit))

    ranked_candidates = evaluate_commits(preprocessed_commits, advisory_record, None)

    ConsoleWriter.print("Commit ranking and aggregation...")
    # I NEED TO GET THE FIRST REACHABLE TAG OR NO-TAG
    ranked_candidates = tag_and_aggregate_commits(ranked_candidates, None)
    ConsoleWriter.print_(MessageStatus.OK)

    return ranked_candidates, advisory_record


# @profile
@measure_execution_time(execution_statistics, name="core")
def prospector(  # noqa: C901
    vulnerability_id: str,
    repository_url: str,
    publication_date: str = "",
    vuln_descr: str = "",
    # tag_interval: str = "",
    version_interval: str = "",
    modified_files: Set[str] = set(),
    advisory_keywords: Set[str] = set(),
    time_limit_before: int = TIME_LIMIT_BEFORE,
    time_limit_after: int = TIME_LIMIT_AFTER,
    use_nvd: bool = True,
    nvd_rest_endpoint: str = "",
    fetch_references: bool = False,
    backend_address: str = DEFAULT_BACKEND,
    use_backend: str = "always",
    git_cache: str = "/tmp/git_cache",
    limit_candidates: int = MAX_CANDIDATES,
    rules: List[str] = ["ALL"],
) -> Tuple[List[Commit], AdvisoryRecord]:

    logger.debug(f"time-limit before: {TIME_LIMIT_BEFORE}")
    logger.debug(f"time-limit after: {TIME_LIMIT_AFTER}")
    logger.debug("begin main commit and CVE processing")

    # construct an advisory record
    with ConsoleWriter("Processing advisory") as _:
        advisory_record = build_advisory_record(
            vulnerability_id,
            vuln_descr,
            nvd_rest_endpoint,
            fetch_references,
            use_nvd,
            publication_date,
            set(advisory_keywords),
            set(modified_files),
        )

    fixing_commit = advisory_record.get_fixing_commit()
    if fixing_commit is not None:
        pass
    # obtain a repository object
    repository = Git(repository_url, git_cache)

    with ConsoleWriter("Git repository cloning") as console:
        logger.debug(f"Downloading repository {repository.url} in {repository.path}")
        repository.clone()

        tags = repository.get_tags()

        logger.debug(f"Found tags: {tags}")
        logger.info(f"Done retrieving {repository.url}")

    # if tag_interval and len(tag_interval) > 0:
    #     prev_tag, next_tag = tag_interval.split(":")
    if version_interval and len(version_interval) > 0:
        prev_tag, next_tag = get_possible_tags(tags, version_interval)
        ConsoleWriter.print(f"Found tags: {prev_tag} - {next_tag}")
        ConsoleWriter.print_(MessageStatus.OK)
    else:
        logger.info("No version/tag interval provided")
        console.print("No interval provided", status=MessageStatus.ERROR)
        sys.exit(1)

    # retrieve of commit candidates
    candidates = get_candidates(
        advisory_record,
        repository,
        prev_tag,
        next_tag,
        time_limit_before,
        time_limit_after,
        limit_candidates,
    )

    candidates = filter(candidates)

    with ExecutionTimer(
        core_statistics.sub_collection("commit preprocessing")
    ) as timer:
        with ConsoleWriter("\nPreprocessing commits") as writer:
            try:
                if use_backend != "never":
                    missing, preprocessed_commits = retrieve_preprocessed_commits(
                        repository_url,
                        backend_address,
                        candidates,
                    )
            except requests.exceptions.ConnectionError:
                logger.error(
                    "Backend not reachable",
                    exc_info=get_level() < logging.WARNING,
                )
                if use_backend == "always":
                    print("Backend not reachable: aborting")
                    sys.exit(0)
                print("Backend not reachable: continuing")

            if "missing" not in locals():
                missing = list(candidates.values())
                preprocessed_commits: List[Commit] = list()

            if len(missing) > 0:

                pbar = tqdm(
                    missing,
                    desc="Preprocessing commits",
                    unit="commit",
                )
                with Counter(
                    timer.collection.sub_collection("commit preprocessing")
                ) as counter:
                    counter.initialize("preprocessed commits", unit="commit")
                    for raw_commit in pbar:
                        counter.increment("preprocessed commits")
                        preprocessed_commits.append(make_from_raw_commit(raw_commit))
            else:
                writer.print("\nAll commits found in the backend")

            pretty_log(logger, advisory_record)

            payload = [c.to_dict() for c in preprocessed_commits]

    if len(payload) > 0 and use_backend != "never":
        save_preprocessed_commits(backend_address, payload)
    else:
        logger.warning("Preprocessed commits are not being sent to backend")

    ranked_candidates = evaluate_commits(preprocessed_commits, advisory_record, rules)

    ConsoleWriter.print("Commit ranking and aggregation...")
    ranked_candidates = tag_and_aggregate_commits(ranked_candidates, next_tag)
    ConsoleWriter.print_(MessageStatus.OK)

    return ranked_candidates, advisory_record


def filter(commits: Dict[str, RawCommit]) -> Dict[str, RawCommit]:
    with ConsoleWriter("\nCandidate filtering\n") as console:
        commits, rejected = filter_commits(commits)
        if rejected > 0:
            console.print(f"Dropped {rejected} candidates")
        return commits


def evaluate_commits(commits: List[Commit], advisory: AdvisoryRecord, rules: List[str]):
    with ExecutionTimer(core_statistics.sub_collection("candidates analysis")):
        with ConsoleWriter("Candidate analysis") as _:
            ranked_commits = apply_ranking(apply_rules(commits, advisory, rules=rules))

    return ranked_commits


def tag_and_aggregate_commits(commits: List[Commit], next_tag: str) -> List[Commit]:
    if next_tag is None or next_tag == "":
        return commits

    twin_tags_map = {commit.commit_id: commit.get_tag() for commit in commits}
    tagged_commits = list()
    for commit in commits:
        if commit.has_tag(next_tag):
            commit.tags = [next_tag]
            for twin in commit.twins:
                twin[0] = twin_tags_map.get(twin[1], "no-tag")
            tagged_commits.append(commit)

    # for commit in commits:
    #     if commit.has_tag() and next_tag == commit.get_tag():
    #         for twin in commit.twins:
    #             twin[0] = mapping_dict[twin[1]]

    #         tagged_commits.append(commit)
    # See the order of the tag list in the commits listed as twin to get the correct tag

    return tagged_commits


def retrieve_preprocessed_commits(
    repository_url: str, backend_address: str, candidates: Dict[str, RawCommit]
) -> Tuple[List[RawCommit], List[Commit]]:
    retrieved_commits: List[dict] = list()
    missing: List[RawCommit] = list()

    responses = list()
    for i in range(0, len(candidates), 500):
        args = list(candidates.keys())[i : i + 500]
        r = requests.get(
            f"{backend_address}/commits/{repository_url}?commit_id={','.join(args)}"
        )
        if r.status_code != 200:
            logger.info("One or more commits are not in the backend")
            break  # return list(candidates.values()), list()
        responses.append(r.json())

    retrieved_commits = [commit for response in responses for commit in response]

    logger.info(f"Found {len(retrieved_commits)} preprocessed commits")

    if len(retrieved_commits) != len(candidates):
        missing = [
            candidates[c]
            for c in set(candidates.keys()).difference(
                rc["commit_id"] for rc in retrieved_commits
            )
        ]

        logger.error(f"Missing {len(missing)} commits")
    commits = [Commit.parse_obj(rc) for rc in retrieved_commits]
    # Sets the tags
    # for commit in commits:
    #     commit.tags = candidates[commit.commit_id].tags
    return (missing, commits)


def save_preprocessed_commits(backend_address, payload):
    with ExecutionTimer(core_statistics.sub_collection(name="save commits to backend")):
        with ConsoleWriter("Saving preprocessed commits to backend") as writer:
            logger.debug("Sending preprocessing commits to backend...")
            try:
                r = requests.post(
                    backend_address + "/commits/",
                    json=payload,
                    headers={"Content-type": "application/json"},
                )
                logger.debug(
                    f"Saving to backend completed (status code: {r.status_code})"
                )
            except requests.exceptions.ConnectionError:
                logger.error(
                    "Could not reach backend, is it running?"
                    "The result of commit pre-processing will not be saved."
                    "Continuing anyway.....",
                    exc_info=get_level() < logging.WARNING,
                )
                writer.print(
                    "Could not save preprocessed commits to backend",
                    status=MessageStatus.WARNING,
                )


def get_candidates(
    advisory_record: AdvisoryRecord,
    repository: Git,
    prev_tag: str,
    next_tag: str,
    time_limit_before: int,
    time_limit_after: int,
    limit_candidates: int,
):
    with ExecutionTimer(
        core_statistics.sub_collection(name="retrieval of commit candidates")
    ):

        with ConsoleWriter("Candidate commit retrieval") as writer:

            since = None
            until = None
            if advisory_record.published_timestamp:
                since = advisory_record.published_timestamp - time_limit_before
                until = advisory_record.published_timestamp + time_limit_after

            candidates = repository.create_commits(
                since=since,
                until=until,
                next_tag=next_tag,
                prev_tag=prev_tag,
                filter_extension=advisory_record.files_extension,
            )

            core_statistics.record("candidates", len(candidates), unit="commits")
            logger.info("Found %d candidates" % len(candidates))
        writer.print(f"Found {len(candidates)} candidates")

        if len(candidates) > limit_candidates:
            logger.error(f"Number of candidates exceeds {limit_candidates}, aborting.")

            writer.print(
                f"Found {len(candidates)} candidates, too many to proceed.",
                status=MessageStatus.ERROR,
            )
            writer.print("Please try running the tool again.")
            sys.exit(-1)

    return candidates
