# from dataclasses import asdict
from datamodel.advisory import AdvisoryRecord, buildAdvisoryRecord

# import pytest


def test_advisory_basic():
    ar = AdvisoryRecord("CVE-2015-5612", "https://github.com/abc/xyz")

    assert ar.repository_url == "https://github.com/abc/xyz"
    # assert ar.vulnerability_id == "CVE-2015-5612"
    # assert ar.published_timestamp == "2015-09-04T15:59Z"


advisory_text = """Unspecified vulnerability in Uconnect before 15.26.1, as used
    in certain Fiat Chrysler Automobiles (FCA) from 2013 to 2015 models, allows
    remote attackers in the same cellular network to control vehicle movement,
    cause human harm or physical damage, or modify dashboard settings via
    vectors related to modification of entertainment-system firmware and access
    of the CAN bus due to insufficient \\"Radio security protection,\\" as
    demonstrated on a 2014 Jeep Cherokee Limited FWD."""


def test_extractor_provided_text():

    # rec = AdvisoryRecord(
    #     "CVE-0000-0000", "today", vulnerability_description=advisory_text
    # )
    # processor = AdvisoryFactory()

    record = buildAdvisoryRecord("CVE-2014-0050", vuln_description=advisory_text)
    print(record)

    assert "15.26.1" in record.versions
    assert "15.26" not in record.versions


def test_extractor_nvd():
    record = buildAdvisoryRecord("CVE-2014-0050", query_nvd=True)

    print(record)
    assert "1.3.1" in record.versions
    assert "1.3" not in record.versions
