import re
from typing import Tuple

from processing.constants import RELEVANT_EXTENSIONS


def is_path(token: str) -> bool:
    """
    Checks whether the token is a path
    """
    return "/" in token.rstrip(".,;:?!\"'") or (
        "." in token.rstrip(".,;:?!\"'")
        and token.rstrip(".,;:?!\"'").split(".")[-1] in RELEVANT_EXTENSIONS
    )


def extract_non_nl_terms(description: str) -> Tuple[str, ...]:
    """
    Extract all words (space delimited) which presumably cannot be part of an natural language sentence.
    These are usually code fragments and names of code entities, or paths.
    """

    for word in description.split():
        no_punctation_word = word.rstrip(").,;:?!\"'").lstrip("(")
        contains_non_word_char = re.search(r"\W", no_punctation_word)
        contains_non_initial_upper_case = re.search(r"\B[A-Z]", no_punctation_word)
        if contains_non_initial_upper_case or contains_non_word_char:
            yield word


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
