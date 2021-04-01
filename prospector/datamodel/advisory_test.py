# from dataclasses import asdict
from datamodel.advisory import AdvisoryRecord

# import pytest


def test_advisory_basic():
    ar = AdvisoryRecord("CVE-2015-5612", "https://github.com/abc/xyz")

    # getFromNVD(ar)

    assert ar.repository_url == "https://github.com/abc/xyz"
    # assert ar.vulnerability_id == "CVE-2015-5612"
    # assert ar.published_timestamp == "2015-09-04T15:59Z"
