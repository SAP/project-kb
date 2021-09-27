# from typing import Tuple
# from datamodel import BaseModel
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import requests
from pydantic import BaseModel, Field

import log.util

# from commit_processor.constants import RELEVANT_EXTENSIONS

_logger = log.util.init_local_logger()

# TODO use prospector own NVD feed endpoint
NVD_REST_ENDPOINT = "http://localhost:8000/nvd/vulnerabilities/"


class AdvisoryRecord(BaseModel):
    """
    The advisory record captures all relevant information on the vulnerability advisory
    """

    vulnerability_id: str
    repository_url: str = ""
    published_timestamp: int = 0
    last_modified_timestamp: int = 0
    references: List[str] = Field(default_factory=list)
    references_content: List[str] = Field(default_factory=list)
    advisory_references: List[str] = Field(default_factory=list)
    affected_products: List[str] = Field(default_factory=list)
    description: Optional[str] = ""
    preprocessed_vulnerability_description: str = ""
    relevant_tags: List[str] = None
    versions: List[str] = Field(default_factory=list)
    from_nvd: bool = False
    nvd_rest_endpoint: str = NVD_REST_ENDPOINT
    paths: List[str] = Field(default_factory=list)
    code_tokens: List[str] = Field(default_factory=list)

    def analyze(self, use_nvd: bool = False):
        self.from_nvd = use_nvd

        if self.from_nvd:
            self._get_from_nvd(self.vulnerability_id, self.nvd_rest_endpoint)

        self.versions.extend(
            [v for v in extract_versions(self.description) if v not in self.versions]
        )
        self.affected_products = extract_products(self.description)
        self.paths = extract_path_tokens(self.description)
        self.code_tokens = extract_camelcase_tokens(self.description)

    def _get_from_nvd(self, vuln_id: str, nvd_rest_endpoint: str = NVD_REST_ENDPOINT):
        """
        populate object field using NVD data
        returns: description, published_timestamp, last_modified timestamp, list of links
        """

        try:
            response = requests.get(nvd_rest_endpoint + vuln_id)
            if response.status_code != 200:
                return
            # data = response.json()["result"]["CVE_Items"][0]
            data = response.json()
            self.published_timestamp = int(
                datetime.strptime(
                    data["publishedDate"], r"%Y-%m-%dT%H:%M%z"
                ).timestamp()
            )
            self.last_modified_timestamp = int(
                datetime.strptime(
                    data["lastModifiedDate"], r"%Y-%m-%dT%H:%M%z"
                ).timestamp()
            )

            self.description = data["cve"]["description"]["description_data"][0][
                "value"
            ]
            self.references = [
                r["url"] for r in data["cve"]["references"]["reference_data"]
            ]

        except Exception:
            _logger.error(
                "Could not retrieve vulnerability data from NVD for " + vuln_id,
                exc_info=log.config.level < logging.INFO,
            )


def extract_versions(text) -> "list[str]":
    """
    Extract all versions mentioned in the advisory text
    """
    regex = r"[0-9]{1,}\.[0-9]{1,}[0-9a-z.]*"
    result = re.findall(regex, text)

    return result


def extract_products(text) -> "list[str]":
    """
    Extract product names from advisory text
    """
    # TODO implement this properly
    regex = r"([A-Z]+[a-z\b]+)"
    result = list(set(re.findall(regex, text)))
    return [p for p in result if len(p) > 2]


def extract_camelcase_tokens(text) -> "list[str]":
    """
    Extract camelcase or snake_case elements from advisory text
    """
    regex = r"([A-Za-z]+[a-z\b]+[A-Z]+[a-z\b]+)"
    result = list(set(re.findall(regex, text)))
    # return list(result)
    return [p for p in result if len(p) > 2]
    # return["blaHlafaHlsafs"]


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
    tokens = [t for t in tokens if t != ""]
    paths = []
    for token in tokens:
        contains_path_separators = ("\\" in token) or ("/" in token) or ("." in token)
        separated_with_period = "." in token
        # has_relevant_extension = token.split(".")[-1] in RELEVANT_EXTENSIONS
        is_xml_tag = token.startswith("<")
        is_property = token.endswith("=")
        is_likely_version = token[0].isdigit() and separated_with_period

        # is_path = contains_path_separators or (
        #     has_relevant_extension if strict_extensions else separated_with_period
        # )
        # probably_not_path = is_xml_tag or is_property or not has_relevant_extension or not contains_path_separators or is_likely_version

        if (
            is_property
            or is_xml_tag
            or is_likely_version
            or not contains_path_separators
        ):
            continue

        # if strict_extensions and not has_relevant_extension:
        #     continue

        paths.append(token)

    return paths


@dataclass
class Reference:
    """
    Used for analyzing the references
    """

    url: str
    repo_url: str

    def __post_init__(self):
        # TODO this is not general (the .git suffix can be stripped only for github)
        self.repo_url = re.sub(r"\.git$|/$", "", self.repo_url)

    def is_pull_page(self):
        return self.repo_url + "/pull/" in self.url

    def is_issue_page(self):
        return self.repo_url + "/issues/" in self.url

    def is_tag_page(self):
        return self.repo_url + "/releases/tag/" in self.url

    def is_commit_page(self):
        return self.repo_url + "/commit/" in self.url
