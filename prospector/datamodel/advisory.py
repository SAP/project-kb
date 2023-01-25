import logging
import os
import re
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests
from dateutil.parser import isoparse

from log.logger import get_level, logger, pretty_log
from util.http import extract_from_webpage, fetch_url

from .nlp import (
    extract_affected_filenames,
    extract_products,
    extract_references_keywords,
    extract_words_from_text,
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
    "bugzilla.redhat.com",
    "redhat.com",
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
        references: Dict[str, str] = None,
        affected_products: List[str] = None,
        versions: Dict[str, List[str]] = None,
        files: Set[str] = None,
        keywords: Set[str] = None,
        files_extensions: Set[str] = None,
    ):
        self.cve_id = cve_id
        self.description = description
        self.published_timestamp = published_timestamp
        self.last_modified_timestamp = last_modified_timestamp
        self.references = references or dict()
        self.affected_products = affected_products or list()
        self.versions = versions or dict()
        self.files = files or set()
        self.keywords = keywords or set()
        self.files_extension = files_extensions or set()

    def analyze(
        self,
        fetch_references: bool = True,
    ):

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

        logger.debug("References: " + str(self.references))

        # TODO: I should extract interesting stuff from the references immediately ad maintain them just for a fast lookup
        logger.debug(f"Relevant references: {len(self.references)}")

    def fetch_references(self):
        for reference in list(self.references.keys()):
            ref = (
                extract_references_keywords(fetch_url(reference))
                if ".".join(urlparse(reference).hostname.split(".")[-2:])
                in ALLOWED_SITES
                else ""
            )
            if ref != "" and ref not in self.references:
                self.references.update({ref: reference})

    def parse_references_from_third_party(self):
        """Parse the references from third party sites"""
        for ref in self.search_references_debian_sec_tracker():
            if ref not in self.references:
                self.references[ref] = "security-tracker.debian.org"

    def get_advisory(self):
        data = get_from_local(self.cve_id)
        if not data:
            data = get_from_nvd(self.cve_id)

        if not data:
            raise Exception("Backend error and NVD error. Wrong API key?")

        self.parse_advisory(data)

    def parse_advisory(self, data):
        self.published_timestamp = int(isoparse(data["published"]).timestamp())
        self.last_modified_timestamp = int(isoparse(data["lastModified"]).timestamp())
        self.description = data["descriptions"][0]["value"]
        self.references = {r["url"]: "" for r in data.get("references", [])}
        self.versions = {
            "affected": [
                item.get("versionEndIncluding", item.get("versionStartIncluding"))
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
        self.versions["fixed"] = [v for v in self.versions["fixed"] if v is not None]

    def get_fixing_commit(self) -> List[str]:
        return [
            c.group(1)
            for ref in self.references
            if (c := re.search(r"github\.com\/(?:[\w-]+\/){2}commit\/(\w{6,40})", ref))
        ]

    def search_references_debian_sec_tracker(self) -> List[str]:
        url = "https://security-tracker.debian.org/tracker/"
        content = fetch_url(url + self.cve_id, False)
        if content is None:
            return []

        notes = content.find("pre")
        if notes is not None:
            links = notes.find_all("a", href=True)
            return [a["href"] for a in links]

        return []


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
    description: Optional[str] = None,
    nvd_rest_endpoint: Optional[str] = None,
    fetch_references: bool = False,
    use_nvd: bool = True,
    publication_date: Optional[str] = None,
    advisory_keywords: Set[str] = set(),
    modified_files: Optional[str] = None,
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
        advisory_record.keywords = advisory_keywords

    if modified_files and len(modified_files) > 0:
        advisory_record.files.update(set(modified_files.split(",")))

    logger.debug(f"{advisory_record.keywords=}")
    logger.debug(f"{advisory_record.files=}")

    return advisory_record
