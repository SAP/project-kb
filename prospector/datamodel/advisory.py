# from typing import Tuple
# from datamodel import BaseModel
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests
import requests_cache
from pydantic import BaseModel, Field

import log.util

from .nlp import (
    extract_path_tokens,
    extract_products,
    extract_special_terms,
    extract_versions,
)

ALLOWED_SITES = [
    "for.testing.purposes",
    "lists.apache.org",
    "just.an.example.site",
    "one.more.example.site",
    "non-existing-url.com",  # for testing.
    "jvndb.jvn.jp",  # for trying out: usually does not aviable, but not always, anyway it is a good example
]

_logger = log.util.init_local_logger()

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
    affected_products: List[str] = Field(default_factory=list)
    description: Optional[str] = ""
    preprocessed_vulnerability_description: str = ""
    relevant_tags: List[str] = None
    versions: List[str] = Field(default_factory=list)
    from_nvd: bool = False
    nvd_rest_endpoint: str = NVD_REST_ENDPOINT
    paths: List[str] = Field(default_factory=list)
    keywords: Tuple[str, ...] = Field(default_factory=tuple)

    def analyze(self, use_nvd: bool = False):
        self.from_nvd = use_nvd

        if self.from_nvd:
            self._get_from_nvd(self.vulnerability_id, self.nvd_rest_endpoint)

        self.versions.extend(
            [v for v in extract_versions(self.description) if v not in self.versions]
        )
        self.affected_products = extract_products(self.description)
        self.paths = extract_path_tokens(self.description)
        self.keywords = extract_special_terms(self.description)

        self.references = [
            r for r in self.references if urlparse(r).hostname in ALLOWED_SITES
        ]

        for r in self.references:
            self.references_content.append(fetch_reference_content(r))

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


def fetch_reference_content(reference: str) -> str:

    try:
        session = requests_cache.CachedSession("requests-cache")
        content = session.get(reference).text
    except Exception:
        _logger.debug(f"can not retrieve reference content: {reference}", exc_info=True)
        return False

    return content


# would be used in the future
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
