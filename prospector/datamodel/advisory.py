# from typing import Tuple
# from datamodel import BaseModel
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests
from pydantic import BaseModel, Field

import log.util
from util.collection import union_of
from util.http import fetch_url

from .nlp import (
    extract_path_tokens,
    extract_products,
    extract_special_terms,
    extract_versions,
)

ALLOWED_SITES = [
    "github.com",
    "github.io",
    "apache.org",
    "gitlab.org",
    "cpan.org",
    "gnome.org",
    "gnu.org",
    "nongnu.org",
    "kernel.org",
    "rclone.org",
    "openssl.org",
    "squid-cache.org",
    "ossec.net",
    "readthedocs.io",
    "atlassian.net",
    "jira.atlassian.com",
    "lists.debian.org",
    "access.redhat.com",
    "openstack.org",
    "python.org",
    "pypi.org",
    "for.testing.purposes",  # do not remove this, used in mocks for testing purposes
    "jvndb.jvn.jp",  # for testing: sometimes unreachable
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

    def analyze(self, use_nvd: bool = False, fetch_references=False):
        self.from_nvd = use_nvd

        if self.from_nvd:
            self._get_from_nvd(self.vulnerability_id, self.nvd_rest_endpoint)

        self.versions = union_of(self.versions, extract_versions(self.description))

        self.affected_products = union_of(
            self.affected_products, extract_products(self.description)
        )
        self.paths = union_of(self.paths, extract_path_tokens(self.description))
        self.keywords = union_of(self.keywords, extract_special_terms(self.description))

        _logger.debug("References: " + str(self.references))
        self.references = [
            r for r in self.references if urlparse(r).hostname in ALLOWED_SITES
        ]
        _logger.debug("Relevant references: " + str(self.references))

        if fetch_references:
            for r in self.references:
                ref_content = fetch_url(r)
                if len(ref_content) > 0:
                    _logger.debug("Fetched content of reference " + r)
                    self.references_content.append(ref_content)

    def _get_from_nvd(self, vuln_id: str, nvd_rest_endpoint: str = NVD_REST_ENDPOINT):
        """
        populate object field using NVD data
        returns: description, published_timestamp, last_modified timestamp, list of references
        """

        # TODO check behavior when some of the data attributes of the AdvisoryRecord
        # class contain data (e.g. passed explicitly as input by the useer);
        # In that case, shall the data from NVD be appended to the exiting data,
        # replace it, be ignored?
        # (note: right now, it just replaces it)
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


# would be used in the future
@dataclass
class Reference:
    """
    Used for analyzing the references
    """

    url: str
    repo_url: str

    # TODO we do not need a class for this, this is a collection of
    # functions, with not state at all, they can become part of some
    # other general string analysis module
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
