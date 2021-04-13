# from dataclasses import asdict
from datamodel.advisory import AdvisoryRecord

# import pytest


def test_advisory_basic():
    adv_rec = AdvisoryRecord("CVE-2015-5612", "https://github.com/abc/xyz")

    assert adv_rec.repository_url == "https://github.com/abc/xyz"
    # assert ar.vulnerability_id == "CVE-2015-5612"
    # assert ar.published_timestamp == "2015-09-04T15:59Z"


ADVISORY_TEXT = """Unspecified vulnerability in Uconnect before 15.26.1, as used
    in certain Fiat Chrysler Automobiles (FCA) from 2013 to 2015 models, allows
    remote attackers in the same cellular network to control vehicle movement,
    cause human harm or physical damage, or modify dashboard settings via
    vectors related to modification of entertainment-system firmware and access
    of the CAN bus due to insufficient \\"Radio security protection,\\" as
    demonstrated on a 2014 Jeep Cherokee Limited FWD."""


def test_adv_record_versions():

    record = AdvisoryRecord("CVE-2014-0050", description=ADVISORY_TEXT)
    # print(record)

    assert "15.26.1" in record.versions
    assert "15.26" not in record.versions


def test_adv_record_nvd():
    record = AdvisoryRecord("CVE-2014-0050", from_nvd=True)

    # print(record)
    assert "1.3.1" in record.versions
    assert "1.3" not in record.versions


def test_adv_record_products():
    record = AdvisoryRecord("CVE-XXXX-YYYY", description=ADVISORY_TEXT)

    # print(record)
    assert "Chrysler" in record.affected_products
