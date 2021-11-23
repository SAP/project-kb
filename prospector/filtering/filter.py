from datamodel.commit import Commit


def filter_commits(
    candidates: "list[Commit]",
) -> "list[Commit]":
    """
    Takes in input a set of candidate (datamodel) commits (coming from the commitdb)
    and returns in output a filtered list obtained by discarding the irrelevant
    ones based on different criteria (timestamp of commit compared to advisory record date,
    extensions of the files modified in the commit, and the like)
    """

    # not implemented yet
    return candidates
