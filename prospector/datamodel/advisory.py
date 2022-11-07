import logging
import os
from typing import List, Set, Tuple
from urllib.parse import urlparse

import requests
from dateutil.parser import isoparse

from log.logger import get_level, logger, pretty_log
from util.http import fetch_url

from .nlp import extract_affected_filenames, extract_products, extract_words_from_text

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
NVD_REST_ENDPOINT = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_API_KEY = os.getenv("NVD_API_KEY", "")


class AdvisoryRecord:
    """The advisory record captures all relevant information on the vulnerability advisory"""

    def __init__(
        self,
        cve_id: str,
        description: str = "",
        published_timestamp: int = 0,
        last_modified_timestamp: int = 0,
        references: List[str] = None,
        references_content: List[str] = None,
        affected_products: List[str] = None,
        versions: List[Tuple[str, str]] = None,
        files: Set[str] = None,
        keywords: Set[str] = None,
    ):
        self.cve_id = cve_id
        self.description = description
        self.published_timestamp = published_timestamp
        self.last_modified_timestamp = last_modified_timestamp
        self.references = references or list()
        self.references_content = references_content or list()
        self.affected_products = affected_products or list()
        self.versions = versions or list()
        self.files = files or set()
        self.keywords = keywords or set()

    def analyze(
        self,
        fetch_references: bool = False,
    ):
        self.versions = [
            version for version in self.versions if version[0] != version[1]
        ]
        # self.versions.extend(extract_versions(self.description))
        # self.versions = list(set(self.versions))

        self.affected_products.extend(extract_products(self.description))
        self.affected_products = list(set(self.affected_products))

        # TODO: this could be done on the words extracted from the description
        self.files.update(extract_affected_filenames(self.description))

        self.keywords.update(extract_words_from_text(self.description))

        logger.debug("References: " + str(self.references))
        # TODO: misses something because of subdomains not considered e.g. lists.apache.org

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
    cve_id: str,
    description: str = None,
    nvd_rest_endpoint: str = None,
    fetch_references: bool = False,
    use_nvd: bool = True,
    publication_date: str = None,
    advisory_keywords: Set[str] = None,
    modified_files: Set[str] = None,
    filter_extensions: List[str] = None,
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

    if advisory_keywords and len(advisory_keywords) > 0:
        advisory_record.keywords.update(advisory_keywords)

    if modified_files and len(modified_files) > 0:
        advisory_record.files.update(modified_files)

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
