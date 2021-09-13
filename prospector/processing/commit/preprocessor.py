from datamodel.commit import Commit as DatamodelCommit
from git.git import Commit as GitCommit
from processing.nlp import (
    extract_cve_references,
    extract_ghissue_references,
    extract_jira_references,
)


def preprocess_commit(git_commit: GitCommit) -> DatamodelCommit:
    # TODO need to recheck these docstring, it may contains some outdated info
    """
    This function is responsible of translating a (git)Commit
    into a preprocessed-Commit, that can be saved to the DB
    and later used by the ranking/ML module.

    The structure of this module is straightforward and should
    remain simple and clear for the sake of maintainability
    and extensibility.

    Add as many "extractor" functions as needed below, and call
    them from this function to assign their result to the
    appropriate attribute of the preprocessed Commit.

    Remember to propagate the changes to the DB schema and
    to the save() and lookup() functions of the database module.

    NOTE: don't be confused by the fact that we have two classes
    both named Commit: the one from the git module represents
    a commit as extracted directly from Git, with only minimal post-processing.
    The datamodel.Commit class instead maps one-to-one onto the
    rows of the backend database, and its instances are the input
    to the ranking module (together with an Advisory Record with
    which they must be matched)
    """

    commit_id = git_commit.get_id()
    repository_url = git_commit._repository._url

    result = DatamodelCommit(commit_id=commit_id, repository=repository_url)

    # This is where all the attributes of the preprocessed commit
    # are computed and assigned.
    #
    # Note: all attributes that do not depend on a particular query
    # (that is, that do not depend on a particular Advisory Record)
    # should be computed here so that they can be stored in the db.
    # Space-efficiency is important.

    result.diff = git_commit.get_diff()
    result.hunks = git_commit.get_hunks()
    result.message = git_commit.get_msg()
    result.timestamp = int(git_commit.get_timestamp())
    result.changed_files = git_commit.get_changed_files()
    result.tags = git_commit.get_tags()
    # TODO extract commit tags

    result.jira_refs = list(set(extract_jira_references(result.message)))
    result.ghissue_refs = extract_ghissue_references(result.message)
    result.cve_refs = extract_cve_references(result.message)
    # result.preprocessed_message = ....

    return result
