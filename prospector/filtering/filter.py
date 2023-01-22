from typing import Dict, List, Tuple

from datamodel.commit import Commit
from git.raw_commit import RawCommit

NON_RELEVANT_FILES = [
    "test",
    ".md",
    ".txt",
    ".rst",
    "/docs/",
    ".meta",
    ".utf8",
    "README",
    "LICENSE",
    "CONTRIBUTING",
    "CHANGELOG",
    "AUTHORS",
    "NOTICE",
    "COPYING",
    "CHANGES",
    "STATUS",
]


# TODO: this filtering should be done earlier to avoid useless commit preprocessing
def filter_commits(
    candidates: Dict[str, RawCommit]
) -> Tuple[Dict[str, RawCommit], int]:
    """
    Takes in input a set of candidate (datamodel) commits (coming from the commitdb)
    and returns in output a filtered list obtained by discarding the irrelevant
    ones based on different criteria (timestamp of commit compared to advisory record date,
    extensions of the files modified in the commit, and the like).

    The first return value is the filtered list, the second is the list of rejected commits.
    """
    # MAX_HUNKS = 200
    MAX_FILES = 100
    MAX_MSG_LEN = 5000

    # Merge commits have zero modified files with git log, so we want to consider them
    filtered_candidates = {
        id: commit
        for id, commit in candidates.items()
        if len(commit.changed_files) <= MAX_FILES
        and len(commit.msg) < MAX_MSG_LEN
        and (contains_relevant_files(commit) or len(commit.changed_files) == 0)
    }

    # We remove the useless files so that they will not be considered later in the diffs
    for _, commit in filtered_candidates.items():
        remove_irrelevant_files(commit)

    return filtered_candidates, len(candidates) - len(filtered_candidates)


def contains_relevant_files(commit: Commit) -> bool:
    """
    This function is responsible for checking whether the commit contains
    relevant files, i.e. files that are not in the NON_RELEVANT_FILES list.
    """
    return any(
        file
        for file in commit.changed_files
        if not any(x in file for x in NON_RELEVANT_FILES)
    )


def remove_irrelevant_files(commit: Commit) -> None:
    """
    This function is responsible for removing the non relevant files
    from the commit.
    """
    commit.changed_files = [
        file
        for file in commit.changed_files
        if not any(x in file for x in NON_RELEVANT_FILES)
    ]
