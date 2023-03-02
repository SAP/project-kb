import logging
import os
import re
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import requests
import validators
from dateutil.parser import isoparse

from log.logger import get_level, logger, pretty_log
from util.http import extract_from_webpage, fetch_url, get_urls

from .nlp import (
    extract_affected_filenames,
    extract_products,
    extract_words_from_text,
    find_commits_references,
)

ALLOWED_SITES = [
    "github.com",
    "github.io",
    "apache.org",
    # "issues.apache.org",
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
    "debian.org"
    # "lists.debian.org",
    # "access.redhat.com",
    "openstack.org",
    "python.org",
    "pypi.org",
    "bugzilla.redhat.com",
    # "redhat.com",
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
        references: Dict[str, int] = None,
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
        self.has_fixing_commit = False

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
        for k, v in self.references.items():
            print(k, v)
        logger.debug("References: " + str(self.references))

        # TODO: I should extract interesting stuff from the references immediately ad maintain them just for a fast lookup
        logger.debug(f"Relevant references: {len(self.references)}")

    def fetch_references(self):
        for reference in list(self.references.keys()):
            if validators.url(reference) and any(a in reference for a in ALLOWED_SITES):
                for link in get_urls(reference):
                    if link.startswith("/"):
                        link = "https://github.com" + link

                    if link in self.references:
                        self.references[link] += 1
                    elif link not in self.references:
                        self.references[link] = 1

        for reference in list(self.references.keys()):
            if "/commit/" in reference or "/commits/" in reference:
                continue
            else:
                del self.references[reference]

    def parse_references_from_third_party(self):
        """Parse the references from third party sites"""
        for ref in self.search_references_debian_sec_tracker():
            self.references.setdefault(ref, 1)

        for ref in self.search_references_bugzilla_redhat():
            self.references.setdefault(ref, 1)

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
        self.references = {r["url"]: 1 for r in data.get("references", [])}
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
        self.references = dict(
            sorted(self.references.items(), key=lambda item: item[1], reverse=True)
        )
        if len(self.references) > 5:
            self.references = {k: v for k, v in self.references.items() if v > 1}

        return [
            c.group(1)
            for ref in self.references
            if (c := re.search(r"\/(?:commit|commits)\/(\w{6,40})", ref))
        ]
        # here match only /commit/XXX

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

    def search_references_bugzilla_redhat(self) -> List[str]:
        url = "https://bugzilla.redhat.com/show_bug.cgi?id="

        content = fetch_url(url + self.cve_id, False)
        if content is None:
            return []
        comments = content.find_all("pre", class_="bz_comment_text")
        links = []
        for comment in comments:
            link = comment.find_all("a", href=True)
            links.extend([a["href"] for a in link if a["href"][:4] == "http"])

        return links


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
    fetch_references: bool = True,
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
