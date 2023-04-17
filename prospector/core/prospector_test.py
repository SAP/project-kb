import subprocess

import pytest

from .prospector import prospector

OPENCAST_CVE = "CVE-2021-21318"
OPENCAST_REPO = "https://github.com/opencast/opencast"


def test_prospector_client():
    results, _ = prospector(
        vulnerability_id=OPENCAST_CVE,
        repository_url=OPENCAST_REPO,
        version_interval="9.1:9.2",
        fetch_references=False,
        git_cache="/tmp/gitcache",
        limit_candidates=5000,
    )
    assert results[0].commit_id == "b18c6a7f81f08ed14884592a6c14c9ab611ad450"
