import re

from datamodel.commit import Commit as DatamodelCommit
from git.git import Commit as GitCommit

from .constants import RELEVANT_EXTENSIONS


def preprocess_commit(git_commit: GitCommit) -> DatamodelCommit:
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
    # result = DatamodelCommit(commit_id, repository_url)
    # result.commit_id = commit_id
    # result.repository = repository_url

    # This is where all the attributes of the preprocessed commit
    # are computed and assigned.
    #
    # Note: all attributes that do not depend on a particular query
    # (that is, that do not depend on a particular Advisory Record)
    # should be computed here so that they can be stored in the db.
    # Space-efficiency is important.
    result.diff = git_commit.get_diff()
    result.hunks = git_commit.get_hunks()
    result.hunk_count = len(result.hunks)
    result.message = git_commit.get_msg()
    result.timestamp = git_commit.get_timestamp()

    # TODO extract commit tags

    result.jira_refs = list(set(extract_jira_references(result.message)))
    result.ghissue_refs = extract_ghissue_references(result.message)
    result.cve_refs = extract_cve_references(result.message)
    # result.preprocessed_message = ....

    return result


# ------------------------------------------------------------------------------
# helper functions
# ------------------------------------------------------------------------------


def extract_ghissue_references(text: str) -> "list[str]":
    """
    Extract identifiers that are (=look like) references to GH issues
    """
    return [result.group(0) for result in re.finditer(r"#\d+:?", text)]


def extract_jira_references(text: str) -> "list[str]":
    """
    Extract identifiers that point to Jira tickets
    """
    return [result.group(0) for result in re.finditer(r"\w+-\d+:?", text)]


def extract_cve_references(text: str) -> "list[str]":
    """
    Extract CVE identifiers
    """
    return [result.group(0) for result in re.finditer(r"CVE-\d{4}-\d{4,8}:?", text)]


###
### NOTE: the following might need to be moved closer to datamodel.advisory
###
def is_path(token: str) -> bool:
    """
    Checks whether the token is a path
    """
    return "/" in token.rstrip(".,;:?!\"'") or (
        "." in token.rstrip(".,;:?!\"'")
        and token.rstrip(".,;:?!\"'").split(".")[-1] in RELEVANT_EXTENSIONS
    )


def extract_code_tokens(description: str) -> "list[str]":
    """
    Extract code tokens from the description: tokens that are either dot.case,
    snake_case or CamelCase and no path (paths are used in a different feature)
    """
    tokens = [
        token.rstrip(".,;:?!\"'") for token in description.split(" ")
    ]  # remove punctuation etc.
    relevant_tokens = [
        token
        for token in tokens
        if not is_path(token)
        and (
            dot_case_split(token) or snake_case_split(token) or camel_case_split(token)
        )
    ]
    return relevant_tokens


def camel_case_split(token: str) -> "list[str]":
    """
    Splits a CamelCase token into a list of tokens, including the original unsplit.

    example: 'CamelCase' --> ['CamelCase', 'camel', 'case']
    """
    matches = re.finditer(
        ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", token
    )
    result = [m.group(0).lower() for m in matches]
    if len(result) == 1:
        return []
    return [token] + result


def snake_case_split(token: str) -> "list[str]":
    """
    Splits a snake_case token into a list of tokens, including the original unsplit.

    Example: 'snake_case' --> ['snake_case', 'snake', 'case']
    """
    result = token.split("_")
    if len(result) == 1:
        return []
    return [token] + result


def dot_case_split(token: str) -> "list[str]":
    """
    Splits a dot.case token into a list of tokens, including the original unsplit.

    Example: 'dot.case' --> ['dot.case', 'dot', 'case']
    """

    result = token.split(".")
    if len(result) == 1:
        return []
    return [token] + result
