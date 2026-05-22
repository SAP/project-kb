# flake8: noqa
import logging
import os
import re
from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests
import validators
from dateutil.parser import isoparse

from llm.llm_service import LLMService
from log.logger import get_level, logger, pretty_log
from util.http import extract_from_webpage, fetch_url, get_urls

from .nlp import (
    extract_affected_filenames,
    extract_products,
    extract_words_from_text,
    find_commits_references,
)

ALLOWED_SITES = [
    "\w+\.apache\.org",
    "issues\.\w+\.org",
    "issues\.\w+\.com",
    "jira\.\w+\.com",
    "jira\.\w+\.org",
    "lists\.\w+\.org",
    "lists\.\w+\.com",
    "bugs\.\w+\.org",
    "bugs\.\w+\.com",
    "security\.\w+\.org",
    "security\.\w+\.com",
    "access\.redhat\.com",
    "github\.com",
    "github\.io",
    "gitlab\.org",
    "cpan\.org",
    "gnome\.org",
    "gnu\.org",
    "nongnu\.org",
    "kernel\.org",
    "rclone\.org",
    "openssl\.org",
    "squid-cache\.org",
    "ossec\.net",
    "readthedocs\.io",
    "atlassian\.net",
    "openstack\.org",
    "python\.org",
    "pypi\.org",
]


LOCAL_NVD_REST_ENDPOINT = "http://localhost:8000/nvd/vulnerabilities/"
NVD_REST_ENDPOINT = "https://services.nvd.nist.gov/rest/json/cves/2.0"
MITRE_REST_ENDPOINT = "https://cveawg.mitre.org/api/cve/"
NVD_API_KEY = os.getenv("NVD_API_KEY", "")


class AdvisoryRecord:
    """The advisory record captures all relevant information on the vulnerability advisory"""

    def __init__(
        self,
        cve_id: str,
        description: str = "",
        reserved_timestamp: int = 0,
        published_timestamp: int = 0,
        updated_timestamp: int = 0,
        repository_url: str = None,
        references: DefaultDict[str, int] = None,
        affected_products: List[str] = None,
        versions: Dict[str, List[str]] = None,
        files: Set[str] = None,
        keywords: Set[str] = None,
        files_extensions: Set[str] = None,
    ):
        self.cve_id = cve_id
        self.description = description
        self.reserved_timestamp = reserved_timestamp
        self.published_timestamp = published_timestamp
        self.updated_timestamp = updated_timestamp
        self.repository_url = repository_url
        self.references = references or defaultdict(lambda: 0)
        self.affected_products = affected_products or list()
        self.versions = versions or dict()
        self.files = files or set()
        self.keywords = keywords or set()
        self.files_extension = files_extensions or set()
        self.has_fixing_commit = False

    def analyze(self):
        self.affected_products.extend(extract_products(self.description))
        self.affected_products = list(set(self.affected_products))

        files, extension = extract_affected_filenames(self.description)
        self.files_extension = extension
        # TODO: this could be done on the words extracted from the description
        self.files.update(files)

        self.keywords.update(set(extract_words_from_text(self.description)))
        # TODO: misses something because of subdomains not considered e.g. lists.apache.org
        self.parse_references_from_third_party()
        self.fetch_references()

        # for k, v in self.references.items():
        #     print(k, v)
        # logger.debug("References: " + str(self.references))

        # TODO: I should extract interesting stuff from the references immediately ad maintain them just for a fast lookup
        logger.debug(f"Relevant references: {len(self.references)}")

    def fetch_references(self):
        for reference in [r for r in self.references if validators.url(r)]:
            if is_url_allowed(urlparse(reference).netloc):
                for link in get_urls(reference):
                    hash = self.extract_hashes(link)
                    if hash is not None:
                        self.references[hash] += 1

        # self.references = {
        #     k: v
        #     for k, v in self.references.items()
        #     if any(
        #         a in k.casefold() for a in ["commit::", "/pull/", "/issues/", "jira"]
        #     )
        # }

    def parse_references_from_third_party(self):
        """Parse the references from third party sites"""
        for ref in (
            self.search_references_debian() + self.search_references_redhat()
        ):
            # self.references[ref] += 2
            self.references[self.extract_hashes(ref)] += 2

    def get_advisory(self):
        """Fills the advisory record with information obtained from an advisory API."""
        details, metadata = get_from_mitre(self.cve_id)
        if metadata is None:
            raise Exception("MITRE API Error")

        if metadata["state"] == "REJECTED":
            raise Exception("Rejected CVE")

        self.parse_advisory_2(details, metadata)

        # data = get_from_local(self.cve_id)
        # if not data:
        #     data = get_from_nvd(self.cve_id)

        # if not data:
        #     raise Exception("Backend error and NVD error. Wrong API key?")

        # self.parse_advisory(data)

    def parse_advisory(self, data):
        self.published_timestamp = int(isoparse(data["published"]).timestamp())
        self.updated_timestamp = int(isoparse(data["lastModified"]).timestamp())
        self.description = data["descriptions"][0]["value"]
        self.references = defaultdict(
            int, {r["url"]: 2 for r in data.get("references", [])}
        )
        # self.references = defaultdict(
        #     int, {self.extract_hashes(r["url"]): 2 for r in data.get("references", [])}
        # )
        self.versions = {
            "affected": [
                item.get(
                    "versionEndIncluding", item.get("versionStartIncluding")
                )
                for item in data["configurations"][0]["nodes"][0]["cpeMatch"]
            ],  # TODO: can return to tuples
            "fixed": [
                item.get("versionEndExcluding")
                for item in data["configurations"][0]["nodes"][0]["cpeMatch"]
            ],
        }
        self.versions["affected"] = [
            v for v in self.versions["affected"] if v is not None
        ]
        self.versions["fixed"] = [
            v for v in self.versions["fixed"] if v is not None
        ]

    def get_commits_in_advisory_references(self) -> List[str]:
        """Processes the advisory's references to extract commit IDs if
        present. Only keeps the five most important ones.

        Returns:
            A list of references to a commit.
        """
        self.references = dict(
            sorted(
                self.references.items(), key=lambda item: item[1], reverse=True
            )
        )
        limit = 0
        while (
            len([r for r in self.references.keys() if r.startswith("commit::")])
            > 5
        ):
            self.references = {
                k: v
                for k, v in self.references.items()
                if ("commit" in k and v > limit) or ("commit" not in k)
            }
            limit += 1

        # Filter out references that are not commit hashes, eg. commit::master
        return [
            ref.split("::")[1]
            for ref in self.references
            if "commit::" in ref
            and ref.split("::")[1] not in ["master", "main"]
        ]

    def search_references_debian(self) -> List[str]:
        url = "https://security-tracker.debian.org/tracker/"
        content = fetch_url(url + self.cve_id, extract_text=False)
        if content is not None:
            notes = content.find("pre")
            if notes is not None:
                return [a["href"] for a in notes.find_all("a", href=True)]

        return []

    def search_references_redhat(self) -> List[str]:
        url = "https://bugzilla.redhat.com/show_bug.cgi?id="
        content = fetch_url(url + self.cve_id, extract_text=False)
        if content is not None:
            links = [
                c
                for comment in content.find_all("pre", class_="bz_comment_text")
                for c in comment.find_all("a", href=True)
            ]
            return [a["href"] for a in links]
            # for comment in content.find_all("pre", class_="bz_comment_text"):
            #     link = comment.find_all("a", href=True)
            #     links.extend([a["href"] for a in link if a["href"][:4] == "http"])

        return []

    def extract_hashes(
        self, reference: str, filter: bool = False
    ) -> str | None:
        if bool(re.search(r"a=commit;", reference)):
            return "commit::" + re.search(r";h=(\w{6,40})", reference).group(1)

        if bool(re.search(r"(?:commit|commits)\/\w{6,40}", reference)):
            return "commit::" + re.search(
                r"(?:commit|commits)\/(\w{6,40})", reference
            ).group(1)

        if bool(re.search(r"(?:commit|patch)\/\?id=\w{6,40}", reference)):
            return "commit::" + re.search(
                r"(?:commit|patch)\/\?id=(\w{6,40})", reference
            ).group(1)
        if validators.url(reference):
            return reference

        if filter:
            # if any(
            #     a in reference.casefold()
            #     for a in ["/pull/", "/issues/", "jira"]
            # )
            return None
        # validators.url(reference)
        return ""

    def parse_advisory_2(self, details, metadata):
        self.affected_products = [details["affected"][0]["product"]]
        self.versions = dict(details["affected"][0]["versions"][0])
        timestamp_fields = {
            "published_timestamp": "datePublished",
            "updated_timestamp": "dateUpdated",
            "reserved_timestamp": "dateReserved",
        }

        for field, key in timestamp_fields.items():
            timestamp = metadata.get(key)
            setattr(
                self,
                field,
                int(isoparse(timestamp).timestamp()) if timestamp else None,
            )
        if not self.description:
            self.description = details["descriptions"][0]["value"]
        self.references = defaultdict(
            int,
            {self.extract_hashes(r["url"]): 2 for r in details["references"]},
        )


# BETA APIs
def get_from_mitre(cve_id: str):
    try:
        response = requests.get(MITRE_REST_ENDPOINT + cve_id)

        if response.status_code != 200:
            return None, None
        response = response.json()
        return response["containers"]["cna"], response["cveMetadata"]
    except Exception:
        logger.error(
            f"Could not retrieve {cve_id} from the MITRE api",
            exc_info=get_level() < logging.INFO,
        )
        return None, None


def get_from_nvd(cve_id: str):
    """Get an advisory from the NVD dtabase"""
    try:
        headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else None
        params = {"cveId": cve_id}

        response = requests.get(
            NVD_REST_ENDPOINT, headers=headers, params=params
        )

        if response.status_code != 200:
            return None

        return response.json()["vulnerabilities"][0]["cve"]

    except Exception:
        logger.error(
            f"Could not retrieve {cve_id} from the NVD api",
            exc_info=get_level() < logging.INFO,
        )
        return None


def is_url_allowed(url: str) -> bool:
    """Check if a URL is allowed to be fetched"""
    for allowed in ALLOWED_SITES:
        if bool(re.search(allowed, url)):
            return True

    return False


def get_from_local(
    vuln_id: str, nvd_rest_endpoint: str = LOCAL_NVD_REST_ENDPOINT
):
    try:
        response = requests.get(nvd_rest_endpoint + vuln_id)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception:
        return None


def build_advisory_record(
    cve_id: str,
    description: Optional[str] = None,
    nvd_rest_endpoint: Optional[str] = None,
    use_nvd: bool = True,
    publication_date: Optional[str] = None,
    advisory_keywords: Set[str] = set(),
    modified_files: Optional[Set[str]] = None,
) -> AdvisoryRecord:
    advisory_record = AdvisoryRecord(
        cve_id=cve_id,
        description=description,
    )

    try:
        advisory_record.get_advisory()
    except Exception as e:
        logger.error(
            f"Could not retrieve {cve_id}: {e}",
            exc_info=get_level() < logging.INFO,
        )
        return None

    pretty_log(logger, advisory_record)

    advisory_record.analyze()
    logger.debug(f"{advisory_record.keywords=}")

    if publication_date:
        advisory_record.published_timestamp = int(
            isoparse(publication_date).timestamp()
        )

    if len(advisory_keywords) > 0:
        advisory_record.keywords = advisory_keywords

    if modified_files and len(modified_files) > 0:
        advisory_record.files.update(modified_files)

    logger.debug(f"{advisory_record.keywords=}")
    logger.debug(f"{advisory_record.files=}")

    return advisory_record
