# flake8: noqa

import logging
import os
import sys
import time
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse

import requests
from tqdm import tqdm

from cli.console import ConsoleWriter, MessageStatus
from datamodel.advisory import AdvisoryRecord, build_advisory_record
from datamodel.commit import Commit, make_from_raw_commit
from filtering.filter import filter_commits
from git.git import Git
from git.raw_commit import RawCommit
from git.version_to_tag import get_possible_tags
from llm.llm_service import LLMService
from log.logger import get_level, logger, pretty_log
from rules.rules import RULES_PHASE_1, apply_rules
from stats.execution import (
    Counter,
    ExecutionTimer,
    execution_statistics,
    measure_execution_time,
)

# Average distance is -202 days (with commit being authored before the vulnerability usually)
# Standard deviation is 422 days
# An ideal search range would be 2 years before and 1 year after (max). However practically this could give

SECS_PER_DAY = 86400
TIME_LIMIT_BEFORE = 60 * SECS_PER_DAY
TIME_LIMIT_AFTER = 60 * SECS_PER_DAY
THREE_YEARS = 3 * 365 * SECS_PER_DAY
ONE_YEAR = 365 * SECS_PER_DAY

MAX_CANDIDATES = 2000
DEFAULT_BACKEND = "http://localhost:8000"
USE_BACKEND_ALWAYS = "always"
USE_BACKEND_OPTIONAL = "optional"
USE_BACKEND_NEVER = "never"


core_statistics = execution_statistics.sub_collection("core")


# @profile
@measure_execution_time(execution_statistics, name="core")
def prospector(  # noqa: C901
    vulnerability_id: str,
    repository_url: str = None,
    publication_date: str = "",
    vuln_descr: str = "",
    version_interval: str = "",
    modified_files: Set[str] = set(),
    advisory_keywords: Set[str] = set(),
    time_limit_before: int = TIME_LIMIT_BEFORE,
    time_limit_after: int = TIME_LIMIT_AFTER,
    use_nvd: bool = True,
    nvd_rest_endpoint: str = "",
    backend_address: str = DEFAULT_BACKEND,
    use_backend: str = USE_BACKEND_ALWAYS,
    git_cache: str = "/tmp/git_cache",
    limit_candidates: int = MAX_CANDIDATES,
    enabled_rules: List[str] = [rule.id for rule in RULES_PHASE_1],
    tag_commits: bool = True,
    silent: bool = False,
    use_llm_repository_url: bool = False,
) -> Tuple[List[Commit], AdvisoryRecord] | Tuple[int, int]:
    if silent:
        logger.disabled = True
        sys.stdout = open("/dev/null", "w")

    logger.debug("begin main commit and CVE processing")

    # construct an advisory record
    with ConsoleWriter("Processing advisory") as console:
        advisory_record = build_advisory_record(
            vulnerability_id,
            vuln_descr,
            nvd_rest_endpoint,
            use_nvd,
            publication_date,
            set(advisory_keywords),
            set(modified_files),
        )
    if advisory_record is None:
        return None, -1

    if use_llm_repository_url:
        with ConsoleWriter("LLM Usage (Repo URL)") as console:
            try:
                repository_url = LLMService().get_repository_url(
                    advisory_record.description, advisory_record.references
                )
                console.print(
                    f"\n  Repository URL: {repository_url}",
                    status=MessageStatus.OK,
                )
            except Exception as e:
                logger.error(
                    e,
                    exc_info=get_level() < logging.INFO,
                )
                console.print(
                    e,
                    status=MessageStatus.ERROR,
                )
                sys.exit(1)

    fixing_commit = advisory_record.get_fixing_commit()
    # print(advisory_record.references)
    # obtain a repository object
    repository = Git(repository_url, git_cache)

    with ConsoleWriter("Git repository cloning") as console:
        logger.debug(
            f"Downloading repository {repository.url} in {repository.path}"
        )
        repository.clone()

        tags = repository.get_tags()

        # logger.debug(f"Found tags: {tags}")
        logger.info(f"Done retrieving {repository.url}")

    candidates: Dict[str, RawCommit] = dict()

    if len(fixing_commit) > 0:
        candidates = get_commits_no_tags(repository, fixing_commit)
        if len(candidates) > 0 and any(
            [c for c in candidates if c in fixing_commit]
        ):
            console.print("Fixing commit found in the advisory references\n")
            advisory_record.has_fixing_commit = True

    if len(candidates) == 0:
        if version_interval and len(version_interval) > 0:
            prev_tag, next_tag = get_possible_tags(tags, version_interval)
            if prev_tag == "" and next_tag == "":
                logger.info("Tag mismatch")
                return None, -1
            ConsoleWriter.print(f"Found tags: {prev_tag} - {next_tag}")
            logger.info(f"Found tags: {prev_tag} - {next_tag}")
            ConsoleWriter.print_(MessageStatus.OK)
        else:
            logger.info("No version/tag interval provided")
            console.print("No interval provided", status=MessageStatus.ERROR)
            # Tag Mismatch
            return None, -1

        candidates = get_commits_from_tags(
            advisory_record,
            repository,
            prev_tag,
            next_tag,
            time_limit_before,
            time_limit_after,
        )

    candidates = filter(candidates)

    if len(candidates) > limit_candidates:
        logger.error(
            f"Number of candidates exceeds {limit_candidates}, aborting."
        )

        ConsoleWriter.print(
            f"Candidates limitlimit exceeded: {len(candidates)}."
        )
        return None, len(candidates)

    with ExecutionTimer(
        core_statistics.sub_collection("commit preprocessing")
    ) as timer:
        with ConsoleWriter("\nProcessing commits") as writer:
            try:
                if use_backend != USE_BACKEND_NEVER:
                    missing, preprocessed_commits = (
                        retrieve_preprocessed_commits(
                            repository_url,
                            backend_address,
                            candidates,
                        )
                    )
            except requests.exceptions.ConnectionError:
                logger.error(
                    "Backend not reachable",
                    exc_info=get_level() < logging.WARNING,
                )
                if use_backend == USE_BACKEND_ALWAYS:
                    if not is_correct_backend_url(backend_address):
                        print(
                            "The backend address should be 'backend:8000' when running the containerised version of Prospector, and 'localhost:8000' otherwise: Aborting."
                        )
                    sys.exit(1)
                print("Backend not reachable: Continuing.")

            if "missing" not in locals():
                missing = list(candidates.values())
                preprocessed_commits: List[Commit] = list()

            if len(missing) > 0:
                # preprocessed_commits += preprocess_commits(missing, timer)

                pbar = tqdm(
                    missing,
                    desc="Processing commits",
                    unit="commit",
                    disable=silent,
                )
                start_time = time.time()
                with Counter(
                    timer.collection.sub_collection("commit preprocessing")
                ) as counter:
                    counter.initialize("preprocessed commits", unit="commit")
                    for raw_commit in pbar:
                        counter.increment("preprocessed commits")
                        # if you want tagging set get_tags=True (slows down)
                        preprocessed_commits.append(
                            make_from_raw_commit(raw_commit, tag_commits)
                        )
                elapsed_time = time.time() - start_time
                if elapsed_time > 1800:
                    logger.error("Processing timeout")
                    return None, len(candidates)

            else:
                writer.print("\nAll commits found in the backend")

            pretty_log(logger, advisory_record)

            payload = [c.to_dict() for c in preprocessed_commits]

    if (
        len(payload) > 0
        and use_backend != USE_BACKEND_NEVER
        and len(missing) > 0
    ):
        save_preprocessed_commits(backend_address, payload)
    else:
        logger.warning("Preprocessed commits are not being sent to backend")

    ranked_candidates = evaluate_commits(
        preprocessed_commits, advisory_record, backend_address, enabled_rules
    )

    # ConsoleWriter.print("Commit ranking and aggregation...")
    ranked_candidates = remove_twins(ranked_candidates)
    # ranked_candidates = tag_and_aggregate_commits(ranked_candidates, next_tag)
    ConsoleWriter.print_(MessageStatus.OK)

    return ranked_candidates, advisory_record


def preprocess_commits(
    commits: List[RawCommit], timer: ExecutionTimer
) -> List[Commit]:
    preprocessed_commits: List[Commit] = list()
    with Counter(
        timer.collection.sub_collection("commit preprocessing")
    ) as counter:
        counter.initialize("preprocessed commits", unit="commit")
        for raw_commit in tqdm(
            commits,
            desc="Processing commits",
            unit=" commit",
        ):
            counter.increment("preprocessed commits")
            counter_val = counter.__dict__["collection"][
                "preprocessed commits"
            ][0]
            if counter_val % 100 == 0 and counter_val * 2 > time.time():
                pass
            preprocessed_commits.append(make_from_raw_commit(raw_commit))
    return preprocessed_commits


def filter(commits: Dict[str, RawCommit]) -> Dict[str, RawCommit]:
    with ConsoleWriter("\nCandidate filtering") as console:
        commits, rejected = filter_commits(commits)
        if rejected > 0:
            console.print(f"Dropped {rejected} candidates")
        return commits


def evaluate_commits(
    commits: List[Commit],
    advisory: AdvisoryRecord,
    backend_address: str,
    enabled_rules: List[str],
) -> List[Commit]:
    """This method applies the rule phases. Each phase is associated with a set of rules:
        - Phase 1: Original rules
        - Phase 2: Rules using the LLMService

    Args:
        commits: the list of candidate commits that rules hsould be applied to
        advisory: the object contianing all information about the advisory
        enabled_rules: a (sub)set of rules to run (to set in config.yaml)

    Returns:
        a list of commits ranked according to their relevance score

    Raises:
        MissingMandatoryValue: if there is an error in the LLM configuration object
    """
    with ExecutionTimer(core_statistics.sub_collection("candidates analysis")):
        with ConsoleWriter("Candidate analysis") as _:
            ranked_commits = apply_rules(
                commits, advisory, backend_address, enabled_rules=enabled_rules
            )

    return ranked_commits


def remove_twins(commits: List[Commit]) -> List[Commit]:
    global_twins_list = set()
    output = list()
    for commit in list(commits):
        if commit.commit_id not in global_twins_list:
            output.append(commit)

            for twin in commit.twins:
                global_twins_list.add(twin[1])

    return output


def tag_and_aggregate_commits(
    commits: List[Commit], next_tag: str
) -> List[Commit]:
    return commits
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

    retrieved_commits = [
        commit for response in responses for commit in response
    ]

    logger.info(f"Found {len(retrieved_commits)} preprocessed commits")

    if len(retrieved_commits) != len(candidates):
        missing = [
            candidates[c]
            for c in set(candidates.keys()).difference(
                rc["commit_id"] for rc in retrieved_commits
            )
        ]

        logger.info(f"{len(missing)} commits not found in backend")
    commits = [Commit.parse_obj(rc) for rc in retrieved_commits]
    # Sets the tags
    # for commit in commits:
    #     commit.tags = candidates[commit.commit_id].tags
    return (missing, commits)


def save_preprocessed_commits(backend_address, payload):
    with ExecutionTimer(
        core_statistics.sub_collection(name="save commits to backend")
    ):
        with ConsoleWriter("Saving processed commits to backend") as writer:
            logger.debug("Sending processing commits to backend...")
            try:
                # logger.debug(
                #     f"the address: {backend_address}, the payload: {payload}"
                # ) # Sanity Check
                r = requests.post(
                    backend_address + "/commits/",
                    json=payload,
                    headers={"Content-type": "application/json"},
                )
                r.raise_for_status()  # Throw exception if not status 200
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
            except requests.exceptions.HTTPError as e:
                logger.error(
                    f"Could not reach backend, request returned with: {e}."
                )
                writer.print(
                    "Could not save preprocessed commits to backend",
                    status=MessageStatus.WARNING,
                )


# tries to be dynamic
# def get_candidates(
#     advisory_record: AdvisoryRecord,
#     repository: Git,
#     prev_tag: str,
#     next_tag: str,
#     time_limit_before: int,
#     time_limit_after: int,
# ):
#     candidates = filter(
#         get_commits(
#             advisory_record,
#             repository,
#             prev_tag,
#             next_tag,
#             time_limit_before,
#             time_limit_after,
#         )
#     )


def get_commits_from_tags(
    advisory_record: AdvisoryRecord,
    repository: Git,
    prev_tag: str,
    next_tag: str,
    time_limit_before: int,
    time_limit_after: int,
):
    with ExecutionTimer(
        core_statistics.sub_collection(name="retrieval of commit candidates")
    ):
        with ConsoleWriter("Candidate commit retrieval") as writer:
            since = None
            until = None
            if (
                advisory_record.published_timestamp
                and not next_tag
                and not prev_tag
            ):
                since = advisory_record.reserved_timestamp - time_limit_before
                until = advisory_record.reserved_timestamp + time_limit_after

            candidates = repository.create_commits(
                since=since,
                until=until,
                next_tag=next_tag,
                prev_tag=prev_tag,
                filter_extension=advisory_record.files_extension,
            )

            if len(candidates) == 0:
                candidates = repository.create_commits(
                    since=advisory_record.reserved_timestamp
                    - time_limit_before,
                    until=advisory_record.reserved_timestamp + time_limit_after,
                    next_tag=None,
                    prev_tag=None,
                    filter_extension=advisory_record.files_extension,
                )
            core_statistics.record(
                "candidates", len(candidates), unit="commits", overwrite=True
            )
            logger.info(f"Found {len(candidates)} candidates")
        writer.print(f"Found {len(candidates)} candidates")

    return candidates


def get_commits_no_tags(repository: Git, commit_ids: List[str]):
    candidates: Dict[str, RawCommit] = dict()

    for commit_id in set(commit_ids):
        candidates = candidates | repository.find_commits_for_twin_lookups(
            commit_id=commit_id
        )

    return candidates


def is_correct_backend_url(backend_url: str) -> bool:
    """Returns True if the backend URL set in the config file matches the way prospector is run. Returns False if
    - Prospector is run containerised and backend_url is not 'backend:8000'
    - Prospector is run locally and backend_url is not 'localhost:8000'
    """
    parsed_config_url = urlparse(backend_url)
    parsed_default_url = urlparse(DEFAULT_BACKEND)

    if parsed_config_url.port != 8000:
        return False

    in_container = os.environ.get("IN_CONTAINER", "") == "1"

    if in_container:
        if parsed_config_url.hostname != "backend":
            return False
    else:
        if parsed_config_url.hostname != parsed_default_url.hostname:
            return False

    return True


# def prospector_find_twins(
#     advisory_record: AdvisoryRecord,
#     repository: Git,
#     commit_ids: List[str],
#     backend_address: str = DEFAULT_BACKEND,
#     use_backend: str = "always",
# ):
#     commits: Dict[str, RawCommit] = dict()

#     # tags = repository.get_tags()
#     for commit_id in set(commit_ids):
#         commits = commits | repository.find_commits_for_twin_lookups(
#             commit_id=commit_id
#         )

#     commits = filter(commits)

#     if use_backend != "never":
#         missing, preprocessed_commits = retrieve_preprocessed_commits(
#             repository.url,
#             backend_address,
#             commits,
#         )

#     # preprocessed_commits = [
#     #     make_from_raw_commit(raw_commit) for raw_commit in commits.values()
#     # ]

#     preprocessed_commits = list()
#     pbar = tqdm(
#         list(commits.values()),
#         desc="Searching twins",
#         unit="commit",
#     )
#     for raw_commit in pbar:
#         preprocessed_commits.append(make_from_raw_commit(raw_commit))

#     if len(preprocessed_commits) > 0 and use_backend != "never":
#         save_preprocessed_commits(
#             backend_address, [c.to_dict() for c in preprocessed_commits]
#         )

#     ranked_candidates = evaluate_commits(preprocessed_commits, advisory_record, ["ALL"])

#     # ConsoleWriter.print("Commit ranking and aggregation...")
#     # I NEED TO GET THE FIRST REACHABLE TAG OR NO-TAG
#     # ranked_candidates = tag_and_aggregate_commits(ranked_candidates, None)
#     # ConsoleWriter.print_(MessageStatus.OK)

#     return ranked_candidates[:100], advisory_record
