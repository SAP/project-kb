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
    return list(set(re.findall(r"(\d+(?:\.\d+)+)", text)))  # Should be more accurate
    # return re.findall(r"[0-9]+\.[0-9]+[0-9a-z.]*", text)


def extract_products(text: str) -> List[str]:
    """
    Extract product names from advisory text
    """
    # TODO implement this properly
    regex = r"([A-Z]+[a-z\b]+)"
    result = list(set(re.findall(regex, text)))
    return [p for p in result if len(p) > 2]


def extract_affected_filenames(
    text: str, extensions: List[str] = RELEVANT_EXTENSIONS
) -> List[str]:
    paths = set()
    for word in text.split():
        res = word.strip("_,.:;-+!?()]}@'\"")
        res = extract_filename_from_path(res)
        res = check_file_class_method_names(res, extensions)
        if res:
            paths.add(res)

    return list(paths)


# TODO: enhanche this
# Now we just try a split by / and then we pass everything to the other checker, it might be done better
def extract_filename_from_path(text: str) -> str:
    return text.split("/")[-1]
    # Pattern //path//to//file or \\path\\to\\file, extract file
    # res = re.search(r"^(?:(?:\/{,2}|\\{,2})([\w\-\.]+))+$", text)
    # if res:
    #     return res.group(1)


def check_file_class_method_names(text: str, relevant_extensions: List[str]) -> str:
    # Covers cases file.extension if extension is relevant, extensions come from CLI parameter
    extensions_regex = r"^([\w\-]+)\.({})?$".format("|".join(relevant_extensions))
    res = re.search(extensions_regex, text)
    if res:
        return res.group(1)

    # Covers cases like: class::method, class.method,
    res = re.search(r"^(\w+)(?:\.|:{2})(\w+)$", text)  # ^(\w{2,})(?:\.|:{2})(\w{2,})$
    # Check if it is not a number
    if res and not bool(re.match(r"^\d+$", res.group(1))):
        return res.group(1)

    # Covers cases like: className or class_name (normal string with underscore), this may have false positive but often related to some code
    if bool(re.search(r"[a-z]{2}[A-Z]+[a-z]{2}", text)) or "_" in text:
        return text

    return None


# def check_unusual_stuff(text: str) -> bool:
#     return '"' in text or "," in text


# def check_if_path(text: str) -> bool:
#     return "/" in text or "\\" in text


# # TODO: look if there are others
# def check_if_file(text: str) -> str:
#     file = text.split(".")
#     if len(file) == 1:
#         file = file[0].split("::")

#     flag = False
#     # Is a filename with extension
#     # TODO: dynamic extension using the --filter-extensions from CLI to reduce computations
#     if file[-1] in RELEVANT_EXTENSIONS:
#         return file[0]

#     # Common name pattern for files or methods with underscores
#     if "_" in file[0] or "_" in file[-1]:
#         return True

#     # Contains "." or "::" can be a Class.Method (Class::Method), letters only
#     if ("." in text or "::" in text) and file[0].isalpha():
#         return True
#     # Contains UPPERCASE and lowercase letters excluding the first and last
#     if bool(re.match(r"(?=.*[a-z])(?=.*[A-Z])", file[0][1:-1])) or bool(
#         re.match(r"(?=.*[a-z])(?=.*[A-Z])", file[-1][1:-1])
#     ):
#         return True

#     return flag


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
        content = fetch_url(JIRA_ISSUE_URL + id, False)
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
