import re
from typing import List, Tuple

from processing.constants import RELEVANT_EXTENSIONS


def extract_non_nl_terms(description: str) -> Tuple[str, ...]:
    """
    Extract all words (space delimited) which presumably cannot be part of an natural language sentence.
    These are usually code fragments and names of code entities, or paths.
    """

    result = []
    for word in description.split():
        no_punctation_word = word.rstrip(").,;:?!\"'").lstrip("(")
        contains_non_word_char = re.search(r"\W", no_punctation_word)
        contains_non_initial_upper_case = re.search(r"\B[A-Z]", no_punctation_word)
        if contains_non_initial_upper_case or contains_non_word_char:
            result.append(word)
    return tuple(result)


def extract_versions(text: str) -> List[str]:
    """
    Extract all versions mentioned in the text
    """
    return re.findall(r"[0-9]+\.[0-9]+[0-9a-z.]*", text)


def extract_products(text: str) -> List[str]:
    """
    Extract product names from advisory text
    """
    # TODO implement this properly
    regex = r"([A-Z]+[a-z\b]+)"
    result = list(set(re.findall(regex, text)))
    return [p for p in result if len(p) > 2]


def extract_path_tokens(text: str, strict_extensions: bool = False) -> List[str]:
    """
    Used to look for paths in the text (i.e. vulnerability description)

    Input:
        text (str)
        strict_extensions (bool): this function will always extract tokens with (back) slashes,
            but it will only match single file names if they have the correct extension, if this argument is True

    Returns:
        list: a list of paths that are found
    """
    tokens = re.split(r"\s+", text)  # split the text into words
    tokens = [
        token.strip(",.:;-+!?)]}'\"") for token in tokens
    ]  # removing common punctuation marks
    paths = []
    for token in tokens:
        contains_path_separators = ("\\" in token) or ("/" in token)
        separated_with_period = "." in token
        has_relevant_extension = token.split(".")[-1] in RELEVANT_EXTENSIONS
        is_xml_tag = token.startswith("<")
        is_property = token.endswith("=")

        is_path = contains_path_separators or (
            has_relevant_extension if strict_extensions else separated_with_period
        )
        probably_not_path = is_xml_tag or is_property
        if is_path and not probably_not_path:
            paths.append(token)
    return paths


def extract_ghissue_references(text: str) -> List[str]:
    """
    Extract identifiers that are (=look like) references to GH issues
    """
    return [result.group(0) for result in re.finditer(r"#\d+", text)]


def extract_jira_references(text: str) -> List[str]:
    """
    Extract identifiers that point to Jira tickets
    """
    return [result.group(0) for result in re.finditer(r"\w+-\d+", text)]


def extract_cve_references(text: str) -> List[str]:
    """
    Extract CVE identifiers
    """
    return [result.group(0) for result in re.finditer(r"CVE-\d{4}-\d{4,8}", text)]
