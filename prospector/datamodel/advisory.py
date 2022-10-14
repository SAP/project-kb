# from typing import Tuple
# from datamodel import BaseModel
import logging
from dateutil.parser import isoparse
from typing import List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests
from pydantic import BaseModel, Field

from log.logger import logger
from util.collection import union_of
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
    "for.testing.purposes",  # do not remove this, used in mocks for testing purposes
    "jvndb.jvn.jp",  # for testing: sometimes unreachable
]


LOCAL_NVD_REST_ENDPOINT = "http://localhost:8000/nvd/vulnerabilities/"
NVD_REST_ENDPOINT = "https://services.nvd.nist.gov/rest/json/cves/2.0?cveId="


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
        self,
        use_nvd: bool = False,
        fetch_references: bool = False,
        relevant_extensions: List[str] = [],
    ):
        self.from_nvd = use_nvd
        if self.from_nvd:
            self.get_advisory(self.vulnerability_id, self.nvd_rest_endpoint)

        self.versions = union_of(self.versions, extract_versions(self.description))
        self.affected_products = union_of(
            self.affected_products, extract_products(self.description)
        )
        # TODO: use a set where possible to speed up the rule application time
        self.paths.update(
            extract_affected_filenames(
                self.description, relevant_extensions
            )  # TODO: this could be done on the words extracted from the description
        )

        self.keywords.update(extract_nouns_from_text(self.description))

        logger.debug("References: " + str(self.references))
        self.references = [
            r for r in self.references if urlparse(r).hostname in ALLOWED_SITES
        ]
        logger.debug("Relevant references: " + str(self.references))
        if fetch_references:
            for r in self.references:
                ref_content = fetch_url(r)
                if len(ref_content) > 0:
                    logger.debug("Fetched content of reference " + r)
                    self.references_content.append(ref_content)

    # TODO check behavior when some of the data attributes of the AdvisoryRecord
    # class contain data (e.g. passed explicitly as input by the useer);
    # In that case, shall the data from NVD be appended to the exiting data,
    # replace it, be ignored? (note: right now, it just replaces it)
    def get_advisory(
        self, vuln_id: str, nvd_rest_endpoint: str = LOCAL_NVD_REST_ENDPOINT
    ):
        """
        populate object field using NVD data
        returns: description, published_timestamp, last_modified timestamp, list of references
        """

        if not self.get_from_local_db(vuln_id, nvd_rest_endpoint):
            self.get_from_nvd(vuln_id)

    # TODO: refactor this stuff
    def get_from_local_db(
        self, vuln_id: str = "", nvd_rest_endpoint: str = LOCAL_NVD_REST_ENDPOINT
    ):
        """
        Get an advisory from the local NVD database
        """
        try:
            response = requests.get(nvd_rest_endpoint + vuln_id)
            if response.status_code != 200:
                return False
            data = response.json()
            self.published_timestamp = int(isoparse(data["publishedDate"]).timestamp())
            self.last_modified_timestamp = int(
                isoparse(data["lastModifiedDate"]).timestamp()
            )

            self.description = data["cve"]["description"]["description_data"][0][
                "value"
            ]
            self.references = [
                r["url"] for r in data["cve"]["references"]["reference_data"]
            ]
            return True
        except Exception as e:
            # Might fail either or json parsing error or for connection error
            logger.error(
                f"Could not retrieve {vuln_id} from the local database",
                exc_info=log.config.level < logging.INFO,
            )
            return False

    def get_from_nvd(self, vuln_id: str, nvd_rest_endpoint: str = NVD_REST_ENDPOINT):
        """
        Get an advisory from the NVD dtabase
        """
        try:
            response = requests.get(nvd_rest_endpoint + vuln_id)
            if response.status_code != 200:
                return False
            data = response.json()["vulnerabilities"][0]["cve"]
            self.published_timestamp = int(isoparse(data["published"]).timestamp())

            self.last_modified_timestamp = int(
                isoparse(data["lastModified"]).timestamp()
            )
            self.description = data["descriptions"][0]["value"]
            self.references = [r["url"] for r in data["references"]]
        except Exception as e:
            # Might fail either or json parsing error or for connection error
            logger.error(
                f"Could not retrieve {vuln_id} from the NVD api",
                exc_info=log.config.level < logging.INFO,
            )
            raise Exception(
                f"Could not retrieve {vuln_id} from the NVD api {e}",
            )


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
        vulnerability_id=vulnerability_id,
        repository_url=repository_url,
        description=vuln_descr,
        from_nvd=use_nvd,
        nvd_rest_endpoint=nvd_rest_endpoint,
    )

    logger.pretty_log(advisory_record)
    advisory_record.analyze(
        use_nvd=use_nvd,
        fetch_references=fetch_references,
        relevant_extensions=filter_extensions,
    )
    logger.debug(f"{advisory_record.keywords=}")

    if publication_date != "":
        advisory_record.published_timestamp = int(
            isoparse(publication_date).timestamp()
        )

    if len(advisory_keywords) > 0:
        advisory_record.keywords.update(advisory_keywords)

    if len(modified_files) > 0:
        advisory_record.paths.update(modified_files)

    logger.debug(f"{advisory_record.keywords=}")
    logger.debug(f"{advisory_record.paths=}")

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
