from typing import Set
from urllib.parse import urlparse

import pandas
import requests_cache

import log.util
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit

# from datamodel.commit_features import CommitWithFeatures
from git.git import Git
from processing.constants import ALLOWED_SITES
from util.similarity import (
    damerau_levenshtein_edit_distance,
    jaccard_set_similarity,
    levenshtein_edit_distance,
    otsuka_ochiai_set_similarity,
    sorensen_dice_set_similarity,
)
from util.tokenize import tokenize_non_nl_term

# from util.profile import profile

# TODO move this file to the rules package and rename it to helpers.py

_logger = log.util.init_local_logger()

DAYS_BEFORE = 180
DAYS_AFTER = 365
DAY_IN_SECONDS = 86400


# # _TODO this should be removed (also its invocation from the client)
# def extract_features(
#     commit: Commit, advisory_record: AdvisoryRecord
# ) -> CommitWithFeatures:
#     references_vuln_id = extract_references_vuln_id(commit, advisory_record)
#     time_between_commit_and_advisory_record = (
#         extract_time_between_commit_and_advisory_record(commit, advisory_record)
#     )
#     commit_reachable_from_given_tag = False
#     # repo = Git(advisory_record.repository_url)
#     # repo.clone(skip_existing=True)

#     # for version in advisory_record.versions:
#     #     version_tag = repo.get_tag_for_version(version)
#     #     if is_commit_reachable_from_given_tag(commit, advisory_record, version_tag[0]):
#     #         commit_reachable_from_given_tag = True
#     #         break

#     changes_relevant_path = extract_changed_relevant_paths(commit, advisory_record)
#     other_CVE_in_message = extract_other_CVE_in_message(commit, advisory_record)
#     referred_to_by_pages_linked_from_advisories = (
#         extract_referred_to_by_pages_linked_from_advisories(commit, advisory_record)
#     )
#     referred_to_by_nvd = extract_referred_to_by_nvd(commit, advisory_record)
#     commit_feature = CommitWithFeatures(
#         commit=commit,
#         references_vuln_id=references_vuln_id,
#         time_between_commit_and_advisory_record=time_between_commit_and_advisory_record,
#         changes_relevant_path=changes_relevant_path,
#         other_CVE_in_message=other_CVE_in_message,
#         referred_to_by_pages_linked_from_advisories=referred_to_by_pages_linked_from_advisories,
#         referred_to_by_nvd=referred_to_by_nvd,
#         commit_reachable_from_given_tag=commit_reachable_from_given_tag,
#         similarities_with_changed_files=extract_path_similarities(
#             commit, advisory_record
#         ),
#     )

#     # commit_feature = CommitWithFeatures(
#     #     commit=commit,
#     #     # references_vuln_id=references_vuln_id,
#     #     # time_between_commit_and_advisory_record=time_between_commit_and_advisory_record,
#     #     # changes_relevant_path=changes_relevant_path,
#     #     # other_CVE_in_message=other_CVE_in_message,
#     #     # referred_to_by_pages_linked_from_advisories=referred_to_by_pages_linked_from_advisories,
#     #     referred_to_by_nvd=referred_to_by_nvd,
#     #     # commit_reachable_from_given_tag=commit_reachable_from_given_tag,
#     # )
#     return commit_feature


def extract_references_vuln_id(commit: Commit, advisory_record: AdvisoryRecord) -> bool:
    return advisory_record.vulnerability_id in commit.cve_refs


def extract_time_between_commit_and_advisory_record(
    commit: Commit, advisory_record: AdvisoryRecord
) -> int:
    return commit.timestamp - advisory_record.published_timestamp


def extract_changed_relevant_paths(
    commit: Commit, advisory_record: AdvisoryRecord
) -> Set[str]:
    """
    Return the list of the changed paths (by a commit) that are
    mentioned in the advisory record
    """
    relevant_paths = []
    for advisory_path in advisory_record.paths:
        relevant_paths += filter(
            lambda path: advisory_path in path, commit.changed_files
        )

    return set(relevant_paths)


def extract_other_CVE_in_message(
    commit: Commit, advisory_record: AdvisoryRecord
) -> Set[str]:
    return set(commit.cve_refs) - {advisory_record.vulnerability_id}


def is_commit_in_given_interval(
    version_timestamp: int, commit_timestamp: int, day_interval: int
) -> bool:
    """
    Return True if the commit is in the given interval before or after the timestamp
    """

    if day_interval == 0:
        return version_timestamp == commit_timestamp
    elif day_interval > 0:
        return (
            version_timestamp + day_interval * DAY_IN_SECONDS
            >= commit_timestamp
            >= version_timestamp
        )
    else:
        return (
            version_timestamp + day_interval * DAY_IN_SECONDS
            <= commit_timestamp
            <= version_timestamp
        )


def extract_referred_to_by_nvd(
    commit: Commit, advisory_record: AdvisoryRecord
) -> Set[str]:
    return set(
        filter(
            lambda reference: commit.commit_id[:8] in reference,
            advisory_record.references,
        )
    )


def is_commit_reachable_from_given_tag(
    commit: Commit, advisory_record: AdvisoryRecord, version_tag: str
) -> bool:
    """
    Return True if the commit is reachable from the given tag
    """
    repo = Git(advisory_record.repository_url)
    # repo.clone()

    commit_id = commit.commit_id
    tag_id = repo.get_commit_id_for_tag(version_tag)

    if not repo.get_commits_between_two_commit(
        commit_id, tag_id
    ) and not repo.get_commits_between_two_commit(tag_id, commit_id):
        return False

    return True


def extract_referred_to_by_pages_linked_from_advisories(
    commit: Commit, advisory_record: AdvisoryRecord
) -> Set[str]:
    allowed_references = filter(
        lambda reference: urlparse(reference).hostname in ALLOWED_SITES,
        advisory_record.references,
    )
    session = requests_cache.CachedSession("requests-cache")

    def is_commit_cited_in(reference: str):
        try:
            return commit.commit_id[:8] in session.get(reference).text
        except Exception:
            _logger.debug(f"can not retrieve site: {reference}", exc_info=True)
            return False

    return set(filter(is_commit_cited_in, allowed_references))


def extract_path_similarities(commit: Commit, advisory_record: AdvisoryRecord):
    similarities = pandas.DataFrame(
        columns=[
            "changed file",
            "code token",
            "jaccard",
            "sorensen-dice",
            "otsuka-ochiai",
            "levenshtein",
            "damerau-levenshtein",
            "length diff",
            "inverted normalized levenshtein",
            "inverted normalized damerau-levenshtein",
        ]
    )
    for changed_file_path in commit.changed_files:
        for code_token in advisory_record.code_tokens:
            parts_of_file_path = tokenize_non_nl_term(changed_file_path)
            parts_of_code_token = tokenize_non_nl_term(code_token)
            similarities = similarities.append(
                {
                    "changed file": changed_file_path,
                    "code token": code_token,
                    "jaccard": jaccard_set_similarity(
                        set(parts_of_file_path), set(parts_of_code_token)
                    ),
                    "sorensen-dice": sorensen_dice_set_similarity(
                        set(parts_of_file_path), set(parts_of_code_token)
                    ),
                    "otsuka-ochiai": otsuka_ochiai_set_similarity(
                        set(parts_of_file_path), set(parts_of_code_token)
                    ),
                    "levenshtein": levenshtein_edit_distance(
                        parts_of_file_path, parts_of_code_token
                    ),
                    "damerau-levenshtein": damerau_levenshtein_edit_distance(
                        parts_of_file_path, parts_of_code_token
                    ),
                    "length diff": abs(
                        len(parts_of_file_path) - len(parts_of_code_token)
                    ),
                },
                ignore_index=True,
            )

    levenshtein_max = similarities["levenshtein"].max()
    similarities["inverted normalized levenshtein"] = 1 - (
        similarities["levenshtein"] / levenshtein_max
    )
    damerau_levenshtein_max = similarities["damerau-levenshtein"].max()
    similarities["inverted normalized damerau-levenshtein"] = 1 - (
        similarities["damerau-levenshtein"] / damerau_levenshtein_max
    )
    return similarities
