from typing import Dict, Set

import pandas
from bs4 import BeautifulSoup
import requests

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from git.git import Git
from util.http import fetch_url
from util.similarity import (
    damerau_levenshtein_edit_distance,
    jaccard_set_similarity,
    levenshtein_edit_distance,
    otsuka_ochiai_set_similarity,
    sorensen_dice_set_similarity,
)
from util.tokenize import tokenize_non_nl_term

DAYS_BEFORE = 180
DAYS_AFTER = 365
DAY_IN_SECONDS = 86400


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
) -> Dict[str, str]:
    return dict.fromkeys(set(commit.cve_refs) - {advisory_record.vulnerability_id}, "")


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


# def extract_referred_to_by_pages_linked_from_advisories(
#     commit: Commit, advisory_record: AdvisoryRecord
# ) -> Set[str]:
#     allowed_references = filter(
#         lambda reference: urlparse(reference).hostname in ALLOWED_SITES,
#         advisory_record.references,
#     )
#     session = requests_cache.CachedSession("requests-cache")

#     def is_commit_cited_in(reference: str):
#         try:
#             return commit.commit_id[:8] in session.get(reference).text
#         except Exception:
#             _logger.debug(f"can not retrieve site: {reference}", exc_info=True)
#             return False
#     return set(filter(is_commit_cited_in, allowed_references))


def extract_commit_mentioned_in_linked_pages(
    commit: Commit, advisory_record: AdvisoryRecord
) -> int:

    # TODO: convert advisory.references to a dictionary (the key must be the url,
    # else we cannot say in which side we found a reference to the commit at hand,
    # when we find one);
    # for now, we can only return an integer from this function, but not ideal
    matching_references_count = 0
    for content_of_reference in advisory_record.references_content:
        if commit.commit_id[:8] in content_of_reference:
            matching_references_count += 1

    return matching_references_count


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
        for code_token in advisory_record.keywords:
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


def fetch_candidate_references(commit: Commit) -> Commit:
    # FIXME: this is very ad-hoc for GH issue/PR pages
    for ref, page_content in commit.ghissue_refs.items():
        if page_content is None:
            url = commit.repository + "/pull/" + ref.lstrip("#")
            # Checks if it is a PR or an issue
            if requests.head(url).status_code != 200:
                url = url.replace("pull", "issues")

            raw_page_content = fetch_url(url, False)
            soup = BeautifulSoup(raw_page_content, "html.parser")
            content = ""
            # print(soup.find(class_="comment-body").get_text())
            for comment in soup.find_all(class_="comment-body"):
                content += comment.get_text().replace("\n", "")
            # for comment_block in soup.find_all(
            #    "div", class_=["markdown-body", "markdown-title"]
            # ):
            #    content += comment_block.get_text()
            if len(content) > 0:
                commit.ghissue_refs[ref] = content

    # TODO: also treat JIRA pages
    # TODO: cache BS extracted text (it takes some time...)
    return commit


if __name__ == "__main__":
    from git.git import Git
    from datamodel.commit import make_from_raw_commit

    repo = Git("https://github.com/apache/superset")
    raw = repo.get_commit("465572325b6c880b81189a94a27417bbb592f540")
    repo.clone()
    commit = make_from_raw_commit(raw)
    commit = fetch_candidate_references(commit)
    print(commit.ghissue_refs)
