from typing import Dict, Tuple

from datamodel.commit import Commit
from git.raw_commit import RawCommit

NON_RELEVANT_FILES = [
    "/test/",
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

NON_RELEVANT_MESSAGES = ["Release version"]


def filter_commits(
    candidates: Dict[str, RawCommit]
) -> Tuple[Dict[str, RawCommit], int]:

    # MAX_HUNKS = 200
    MAX_FILES = 100
    MAX_MSG_LEN = 5000

    old_length = len(candidates)
    for commit in list(candidates.keys()):
        if len(candidates[commit].changed_files) > MAX_FILES:
            del candidates[commit]
            # log deletion
        elif len(candidates[commit].msg) > MAX_MSG_LEN:
            del candidates[commit]
            # log deletion
        # Those are merge commits, must be included
        # elif not contains_relevant_files(candidates[commit]):
        #     if candidates[commit].id == "6e46f9e3f014d64dd7d1e258eaf626e39870ee1f":
        #         print("SIMOLA")
        #     del candidates[commit]
        #     # log deletion
        elif (
            not contains_relevant_files(candidates[commit])
            and len(candidates[commit].changed_files) != 0
        ):
            del candidates[commit]
            # log deletion
        else:
            remove_irrelevant_files(candidates[commit])

    # Merge commits have zero modified files with git log, so we want to consider them
    # filtered_candidates = {
    #     id: commit
    #     for id, commit in candidates.items()
    #     if len(commit.changed_files) <= MAX_FILES
    #     and len(commit.msg) < MAX_MSG_LEN
    #     and (contains_relevant_files(commit) or len(commit.changed_files) == 0)
    # }

    # We remove the useless files so that they will not be considered later in the diffs
    # for _, commit in filtered_candidates.items():
    #     remove_irrelevant_files(commit)

    return candidates, len(candidates) - old_length


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
