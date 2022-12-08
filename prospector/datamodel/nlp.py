import os
import re
from typing import Dict, List, Set

import requests

# from util.http import extract_from_webpage, fetch_url, get_from_xml
from spacy import load

from datamodel.constants import RELEVANT_EXTENSIONS
from util.http import get_from_xml

JIRA_ISSUE_URL = "https://issues.apache.org/jira/browse/"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


nlp = load("en_core_web_sm")


def extract_special_terms(description: str) -> Set[str]:
    """
    Extract all words (space delimited) which presumably cannot be part of an natural language sentence.
    These are usually code fragments and names of code entities, or paths.
    """

    return set()
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


def extract_words_from_text(text: str) -> Set[str]:
    """Use spacy to extract "relevant words" from text"""
    # Lemmatization
    return set(
        [
            token.lemma_.casefold()
            for token in nlp(text)
            if token.pos_ in ("NOUN", "VERB", "PROPN") and len(token.lemma_) > 3
        ]
    )


def find_similar_words(adv_words: Set[str], commit_msg: str, exclude: str) -> Set[str]:
    """Extract nouns from commit message that appears in the advisory text"""
    commit_words = {
        word for word in extract_words_from_text(commit_msg) if word not in exclude
    }
    return commit_words.intersection(adv_words)
    # return [word for word in extract_words_from_text(commit_msg) if word in adv_words]


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
    result = set(re.findall(regex, text))
    return [p for p in result if len(p) > 2]


def extract_affected_filenames(
    text: str, extensions: List[str] = RELEVANT_EXTENSIONS
) -> Set[str]:
    files = set()
    for word in text.split():
        res = word.strip("_,.:;-+!?()[]'\"")
        res = extract_filename_from_path(res)
        res = extract_filename(res, extensions)
        if res:
            files.add(res)
    return files


# TODO: enhanche this
# Now we just try a split by / and then we pass everything to the other checker, it might be done better
def extract_filename_from_path(text: str) -> str:
    return text.split("/")[-1]


def extract_filename(text: str, relevant_extensions: List[str]) -> str:
    # Covers cases file.extension if extension is relevant, extensions come from CLI parameter
    extensions_regex = r"^(?:^|\s?)([\w\-]{2,}\.(?:%s))(?:$|\s|\.|,|:)" % "|".join(
        relevant_extensions
    )

    res = re.search(extensions_regex, text)
    if res:
        return res.group(1)

    # Covers cases like: class::method, class.method,
    res = re.search(r"^(\w+)(?:\.|:{2})(\w+)$", text)  # ^(\w{2,})(?:\.|:{2})(\w{2,})$
    # Check if it is not a number
    if res and not bool(re.match(r"^\d+$", res.group(1))):
        return res.group(1)

    # className or class_name (normal string with underscore)
    # TODO: ShenYu and words
    # like this should be excluded...
    if bool(re.search(r"[a-z]{2,}[A-Z]+[a-z]*", text)) or "_" in text:
        return text

    return None


def extract_ghissue_references(repository: str, text: str) -> Dict[str, str]:
    """
    Extract identifiers that look like references to GH issues, then extract their content
    """
    refs = dict()

    # /repos/{owner}/{repo}/issues/{issue_number}
    headers = {
        "Accept": "application/vnd.github+json",
    }
    if GITHUB_TOKEN:
        headers.update({"Authorization": f"Bearer {GITHUB_TOKEN}"})

    for result in re.finditer(r"(?:#|gh-)(\d+)", text):
        id = result.group(1)
        owner, repo = repository.split("/")[-2:]
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{id}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            refs[id] = f"{data['title']} {data['body']}"

    return refs


# TODO: clean jira page content
def extract_jira_references(repository: str, text: str) -> Dict[str, str]:
    """
    Extract identifiers that point to Jira tickets, then extract their content
    """
    refs = dict()
    if "apache" not in repository:
        return refs

    for result in re.finditer(r"[A-Z]+-\d+", text):
        id = result.group()
        issue_content = get_from_xml(id)
        refs[id] = (
            " ".join(re.findall(r"\w{3,}", issue_content))
            if len(issue_content) > 0
            else ""
        )

    return refs


def extract_cve_references(text: str) -> List[str]:
    """
    Extract CVE identifiers
    """
    return [result.group(0) for result in re.finditer(r"CVE-\d{4}-\d{4,8}", text)]
