from typing import List, Tuple

from datamodel.commit import Commit


# TODO: this filtering should be done earlier to avoid useless commit preprocessing
def filter_commits(candidates: List[Commit]) -> Tuple[List[Commit], int]:
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

    filtered_candidates = [
        c
        for c in candidates
        if MIN_HUNKS <= c.get_hunks() <= MAX_HUNKS and len(c.changed_files) <= MAX_FILES
    ]

    rejected = len(candidates) - len(filtered_candidates)

    return filtered_candidates, rejected
