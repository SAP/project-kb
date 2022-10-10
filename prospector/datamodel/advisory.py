import logging
import os
from typing import List, Set, Tuple
from urllib.parse import urlparse

import requests
from pydantic import BaseModel, Field
import spacy

from log.logger import get_level, logger, pretty_log
from util.http import fetch_url

from .nlp import (
    extract_affected_filenames,
    extract_nouns_from_text,
    extract_products,
    extract_special_terms,
    extract_versions,
)

ALLOWED_SITES = [
    "github.com",
    "github.io",
    "apache.org",
    "issues.apache.org",
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
]


LOCAL_NVD_REST_ENDPOINT = "http://localhost:8000/nvd/vulnerabilities/"
NVD_REST_ENDPOINT = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId="


# TODO: refactor and clean
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
    nvd_rest_endpoint: str = LOCAL_NVD_REST_ENDPOINT
    paths: Set[str] = Field(default_factory=set)
    keywords: Set[str] = Field(default_factory=set)

    # def __init__(self, vulnerability_id, repository_url, from_nvd, nvd_rest_endpoint):
    #     self.vulnerability_id = vulnerability_id
    #     self.repository_url = repository_url
    #     self.from_nvd = from_nvd
    #     self.nvd_rest_endpoint = nvd_rest_endpoint

    def analyze(
        self, use_nvd: bool = False, fetch_references: bool = False, relevant_extensions: List[str] = []
    ):
        self.versions = [
            version for version in self.versions if version[0] != version[1]
        ]
        # self.versions.extend(extract_versions(self.description))
        # self.versions = list(set(self.versions))

        self.versions = union_of(self.versions, extract_versions(self.description))
        self.affected_products = union_of(
            self.affected_products, extract_products(self.description)
        )
        # TODO: use a set where possible to speed up the rule application time
        self.paths.update(
            extract_affected_filenames(self.description, relevant_extensions)  # TODO: this could be done on the words extracted from the description
        )

        self.keywords.update(extract_nouns_from_text(self.description))

        _logger.debug("References: " + str(self.references))
        self.references = [
            r
            for r in self.references
            if ".".join(urlparse(r).hostname.split(".")[-2:]) in ALLOWED_SITES
        ]
        logger.debug("Relevant references: " + str(self.references))

        if fetch_references:
            self.references_content = [
                " ".join(str(fetch_url(r)).split()) for r in self.references
            ]

    def get_advisory(self):
        data = get_from_local(self.cve_id) or get_from_nvd(self.cve_id)

        if data is None:
            raise Exception("Backend error and NVD error. Missing API key?")

        self.parse_advisory(data)

    def parse_advisory(self, data):
        self.published_timestamp = int(isoparse(data["published"]).timestamp())
        self.last_modified_timestamp = int(isoparse(data["lastModified"]).timestamp())
        self.description = data["descriptions"][0]["value"]
        self.references = [r["url"] for r in data.get("references", [])]
        self.versions = [
            (
                item.get("versionStartIncluding", item.get("versionStartExcluding")),
                item.get("versionEndExcluding", item.get("versionEndIncluding")),
            )
            for item in data["configurations"][0]["nodes"][0]["cpeMatch"]
        ]


def get_from_nvd(cve_id: str):
    """Get an advisory from the NVD dtabase"""
    try:
        headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else None
        params = {"cveId": cve_id}

        response = requests.get(NVD_REST_ENDPOINT, headers=headers, params=params)

        if response.status_code != 200:
            return None

        return response.json()["vulnerabilities"][0]["cve"]

    except Exception:
        logger.error(
            f"Could not retrieve {cve_id} from the NVD api",
            exc_info=get_level() < logging.INFO,
        )
        return None


def get_from_local(vuln_id: str, nvd_rest_endpoint: str = LOCAL_NVD_REST_ENDPOINT):
    try:
        response = requests.get(nvd_rest_endpoint + vuln_id)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None


def build_advisory_record(
    vulnerability_id: str,
    repository_url: str,
    vuln_descr: str,
    nvd_rest_endpoint: str,
    fetch_references: bool,
    use_nvd: bool,
    publication_date: str,
    advisory_keywords: Set[str],
    modified_files: Set[str],
    filter_extensions: List[str],
) -> AdvisoryRecord:

    advisory_record = AdvisoryRecord(
        cve_id=cve_id,
        description=description,
    )

    if use_nvd:
        advisory_record.get_advisory()

    pretty_log(logger, advisory_record)

    advisory_record.analyze(
        fetch_references=fetch_references,
    )
    logger.debug(f"{advisory_record.keywords=}")

    if publication_date:
        advisory_record.published_timestamp = int(
            isoparse(publication_date).timestamp()
        )

    if len(advisory_keywords) > 0:
        advisory_record.keywords.update(advisory_keywords)

    if len(modified_files) > 0:
        advisory_record.paths.update(modified_files)

    logger.debug(f"{advisory_record.keywords=}")
    logger.debug(f"{advisory_record.files=}")

    return advisory_record


# might be used in the future
# @dataclass
# class Reference:
#     """
#     Used for analyzing the references
#     """

#     url: str
#     repo_url: str

#     # TODO we do not need a class for this, this is a collection of
#     # functions, with not state at all, they can become part of some
#     # other general string analysis module
#     def __post_init__(self):
#         # TODO this is not general (the .git suffix can be stripped only for github)
#         self.repo_url = re.sub(r"\.git$|/$", "", self.repo_url)

#     def is_pull_page(self):
#         return self.repo_url + "/pull/" in self.url

#     def is_issue_page(self):
#         return self.repo_url + "/issues/" in self.url

#     def is_tag_page(self):
#         return self.repo_url + "/releases/tag/" in self.url

#     def is_commit_page(self):
#         return self.repo_url + "/commit/" in self.url
