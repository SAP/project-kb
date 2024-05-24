import re
from typing import Dict, List, Set, Tuple

from spacy import load

from datamodel.constants import RELEVANT_EXTENSIONS
from util.http import fetch_url, get_from_xml

nlp = load("en_core_web_sm")


def get_names(text: str, exclude: str) -> List[str]:
    """
    Extract names from text
    """
    return [
        token.text
        for token in nlp(text)
        if token.pos_ in ("PROPN", "NOUN")
        and token.text.casefold() not in exclude
        and token.is_alpha
    ]


def clean_string(text: str) -> str:
    """
    Remove all non-alphanumeric characters from a string
    """
    return " ".join(
        set(
            [
                token.lemma_
                for token in nlp(text)
                if not token.is_punct and len(token.lemma_) > 2
            ]
        )
    )


def extract_words_from_text(text: str) -> List[str]:
    """Use spacy to extract "relevant words" from text"""
    # Lemmatization
    return [
        token.lemma_.casefold()
        for token in nlp(text)
        if token.pos_ in ("NOUN", "VERB", "PROPN")
        and len(token.lemma_) > 3
        and token.lemma_.isalnum()
    ]


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
    return list(
        set(
            [
                token.text
                for token in nlp(text)
                if token.pos_ in ("PROPN")
                and token.text.isalpha()
                and len(token.text) > 2
            ]
        )  # "NOUN",
    )


# TODO: add list of non-relevant or relevant extensions
def extract_affected_filenames(
    text: str, extensions: List[str] = RELEVANT_EXTENSIONS
) -> Tuple[Set[str], Set[str]]:
    files = set()
    extension = set()
    for word in text.split():
        res = re.sub(r"^[^a-z0-9]+|[^a-z0-9]+$", "", word, flags=re.IGNORECASE)
        res = re.split(r"[\\\/]", res)[-1]
        if res == "Node.js":
            continue
        res, ext = extract_filename(res, extensions)
        if len(res) > 0:
            files.update(res)
        if ext is not None and ext not in ("yml", "yaml", "json", "bat"):
            extension.add(ext)

    return files, extension


# TODO: enhanche this
# Now we just try a split by / and then we pass everything to the other checker, it might be done better
def extract_filename_from_path(text: str) -> str:
    return text.split("/")[-1]


def extract_filename(text: str, relevant_extensions: List[str]) -> List[str]:
    # Covers cases file.extension if extension is relevant, extensions come from CLI parameter
    res = re.search(r"(?:(\w{2,})\.)+(\w+)", text, flags=re.IGNORECASE)
    is_version = re.search(r"(\d+(?:\.\d+)+)", text)
    if res is not None:
        if res.group(2) in relevant_extensions:
            return [res.group(1)], res.group(2)
        elif not res.group(2).isdigit() and not is_version:
            return [res.group(2), res.group(1)], None

    # This regex covers cases with various camelcase filenames and underscore, dash names
    if bool(
        re.search(
            r"(?:[a-z]|[A-Z])[a-zA-Z]+[A-Z]\w*|(?:[a-zA-Z]{2,}[_-])+[a-zA-Z]{2,}", text
        )
    ):
        return [text], None
    return [], None


def extract_ghissue_references(repository: str, text: str) -> Dict[str, str]:
    """
    Extract identifiers that look like references to GH issues, then extract their content
    """
    refs = dict()

    for result in re.finditer(r"(?:#|gh-)(\d{1,6})", text):
        id = result.group(1)
        url = f"{repository}/issues/{id}"
        content = fetch_url(url=url, extract_text=False)
        if content is not None:
            gh_ref_data = content.find_all(
                attrs={
                    "class": ["comment-body", "markdown-title"],
                },
                recursive=False,
            )
            # TODO: when an issue/pr is referenced somewhere, the page contains also the "message" of that reference (e.g. a commit). This may lead to unwanted detection of certain rules.
            gh_ref_data.extend(
                content.find_all(
                    attrs={
                        "id": re.compile(r"ref-issue|ref-pullrequest"),
                    }
                )
            )
            refs[id] = " ".join(
                [" ".join(block.get_text().split()) for block in gh_ref_data]
            )

    return refs


# TODO: clean jira page content
def extract_jira_references(repository: str, text: str) -> Dict[str, str]:
    """
    Extract identifiers that point to Jira tickets, then extract their content
    """
    refs = dict()
    if "apache" not in repository:
        return refs

    for result in re.finditer(r"[A-Z]+-\d{1,6}", text):
        id = result.group()
        if not id.startswith("CVE-"):
            refs[id] = get_from_xml(id)

    return refs


def extract_cve_references(text: str) -> List[str]:
    """
    Extract CVE identifiers
    """
    return list(
        set([result.group(0) for result in re.finditer(r"CVE-\d{4}-\d{4,8}", text)])
    )


def find_commits_references(text: str) -> List[str]:
    # SHould probably look for hrefs too
    # hrefs containing /commit/xxx (handles github issues)
    # in repo names we have to consider also . -
    # github\.com\/[\w\-\.\/]+\/commit\/\w{6,40}
    return [
        res.group(0)
        for res in re.finditer(r"\/commit\/\w{6,40}", text)
        if res is not None
    ]
    result = re.search(
        r"\/commit\/\w{6,40}",
        text,
    )
    if result is not None:
        return result.group(0)
    else:
        return ""
