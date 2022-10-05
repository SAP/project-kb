import re
from typing import Dict, List, Tuple
from util.http import fetch_url


from datamodel.constants import RELEVANT_EXTENSIONS

JIRA_ISSUE_URL = "https://issues.apache.org/jira/browse/"


def extract_special_terms(description: str) -> Tuple[str, ...]:
    """
    Extract all words (space delimited) which presumably cannot be part of an natural language sentence.
    These are usually code fragments and names of code entities, or paths.
    """

    return ()
    # TODO replace this with NLP implementation
    # see, https://github.com/SAP/project-kb/issues/256#issuecomment-927639866
    # noinspection PyUnreachableCode
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


def extract_affected_files_paths(text: str, strict_extensions: bool = False):
    words = text.split()
    words = [
        word.strip("_,.:;-+!?)]}'\"") for word in words
    ]  # removing common punctuation marks
    paths = []
    for word in words:
        is_xml_tag = word.startswith("<")
        is_property = word.endswith("=")
        is_unusual = check_unusual_stuff(word)
        not_relevant = is_xml_tag or is_property or is_unusual

        if not_relevant:
            continue

        if check_if_path(word):
            paths.append(word)

        if check_if_file(word):
            paths.append(word.split(".")[0].split("::")[0])

    return paths


def check_unusual_stuff(text: str) -> bool:
    return '"' in text or "," in text


def check_if_path(text: str) -> bool:
    return "/" in text or "\\" in text


# TODO: look if there are others
def check_if_file(text: str) -> bool:
    file = text.split(".")
    if len(file) == 1:
        file = file[0].split("::")

    flag = False
    # Check if there is an extension
    if file[-1] in RELEVANT_EXTENSIONS:
        return True

    # Common name pattern for files or methods with underscores
    if "_" in file[0] or "_" in file[-1]:
        return True

    # Common methods to refer to methods inside class (e.g. Class.method, Class::method)
    if ("." in text or "::" in text) and file[0].isalpha():
        return True
    # Common name for files or methods with uppercase letter in the middle
    if bool(re.match(r"(?=.*[a-z])(?=.*[A-Z])", file[0][1:])) or bool(
        re.match(r"(?=.*[a-z])(?=.*[A-Z])", file[-1][1:])
    ):
        return True

    return flag


def extract_ghissue_references(repository: str, text: str) -> Dict[str, str]:
    """
    Extract identifiers that look like references to GH issues, then extract their content
    """
    refs = dict()
    for result in re.finditer(r"#\d+|gh-\d+", text):
        id = result.group().lstrip("#")
        url = f"{repository}/issues/{id}"
        content = fetch_url(url, False)
        if not content:
            return {"": ""}
        refs[id] = "".join(
            [
                block.get_text().replace("\n", "")
                for block in content.find_all(
                    attrs={"class": ["comment-body", "markdown-title"]}
                )
            ]
        )
    return refs


def extract_jira_references(repository: str, text: str) -> Dict[str, str]:
    """
    Extract identifiers that point to Jira tickets
    """
    refs = dict()
    for result in re.finditer(r"[A-Z]+-\d+", text):
        id = result.group()
        url = JIRA_ISSUE_URL + id
        content = fetch_url(url, False)
        if not content:
            return {"": ""}
        refs[id] = "".join(
            [
                block.get_text().replace("\n", "")
                for block in content.find_all(
                    # Find correct elemenets
                    attrs={"id": ["details-module", "descriptionmodule"]}
                )
            ]
        )
    return refs


def extract_cve_references(repository: str, text: str) -> List[str]:
    """
    Extract CVE identifiers
    """
    return [result.group(0) for result in re.finditer(r"CVE-\d{4}-\d{4,8}", text)]
