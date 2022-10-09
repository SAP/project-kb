from typing import List, Tuple

from datamodel.commit import Commit


def filter_commits(candidates: List[Commit]) -> Tuple[List[Commit], List[Commit]]:
    """
    Takes in input a set of candidate (datamodel) commits (coming from the commitdb)
    and returns in output a filtered list obtained by discarding the irrelevant
    ones based on different criteria (timestamp of commit compared to advisory record date,
    extensions of the files modified in the commit, and the like).

    The first return value is the filtered list, the second is the list of rejected commits.
    """
    MAX_HUNKS = 200
    MAX_FILES = 100

    MIN_HUNKS = 1

    # TODO: maybe this could become a dictionary, with keys indicating "reasons" for rejection
    # which would enable a more useful output

    rejected = []
    for c in list(candidates):
        if c.hunk_count > MAX_HUNKS or c.hunk_count < MIN_HUNKS:
            candidates.remove(c)
            rejected.append(c)
        if len(c.changed_files) > MAX_FILES:
            candidates.remove(c)
            rejected.append(c)

    return candidates, rejected
