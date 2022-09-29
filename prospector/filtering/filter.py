from typing import List, Tuple

from datamodel.commit import Commit


def filter_commits(
    candidates: "list[Commit]",
) -> Tuple[List[Commit], List[Commit]]:
    """
    Takes in input a set of candidate (datamodel) commits (coming from the commitdb)
    and returns in output a filtered list obtained by discarding the irrelevant
    ones based on different criteria (timestamp of commit compared to advisory record date,
    extensions of the files modified in the commit, and the like).

    The first return value is the filtered list, the second is the list of rejected commits.
    """
    MAX_HUNKS = 200
    MAX_FILES = 100

    # TODO: maybe this could become a dictionary, with keys indicating "reasons" for rejection
    # which would enable a more useful output
    rejected = []

    for c in candidates:
        if len(c.hunks) > MAX_HUNKS:
            rejected.append(c)
        if len(c.changed_files) > MAX_FILES:
            rejected.append(c)

    return [c for c in candidates if c not in rejected], [r.commit_id for r in rejected]
