import time

from datamodel.advisory import AdvisoryRecord, build_advisory_record

ADVISORY_TEXT = """Unspecified vulnerability in Uconnect before 15.26.1, as used
    in certain Fiat Chrysler Automobiles (FCA) from 2013 to 2015 models, allows
    remote attackers in the same cellular network to control vehicle movement,
    cause human harm or physical damage, or modify dashboard settings via
    vectors related to modification of entertainment-system firmware and access
    of the CAN bus due to insufficient \\"Radio security protection,\\" as
    demonstrated on a 2014 Jeep Cherokee Limited FWD."""

ADVISORY_TEXT_2 = """
In Apache Commons IO before 2.7, When invoking the method FileNameUtils.normalize
with an improper input string, like "//../foo", or "\\..\\foo", the result would be
the same value, thus possibly providing access to files in the parent directory,
but not further above (thus "limited" path traversal), if the calling code would
use the result to construct a path value."""

cve_list = """
CVE-2020-13924
CVE-2020-11987
CVE-2020-17516
CVE-2021-25640
CVE-2020-11995
CVE-2021-25646
CVE-2020-13922
CVE-2020-17514
CVE-2020-11997
CVE-2020-9492
CVE-2020-1926
CVE-2020-13950
CVE-2020-35452
CVE-2021-20190
CVE-2020-27223
CVE-2020-9493
CVE-2020-17534
CVE-2021-21295
CVE-2021-25958
CVE-2020-17532
CVE-2020-17523
CVE-2020-1946
CVE-2020-17525
CVE-2020-13949
CVE-2021-25122
CVE-2020-17522
CVE-2020-13936
CVE-2020-13959
CVE-2021-23926
CVE-2020-11988
CVE-2019-10095
CVE-2020-13929"""

test = """The Apache Beam MongoDB connector in versions 2.10.0 to 2.16.0 has an option to disable SSL trust verification. However this configuration is not respected and the certificate verification disables trust verification in every case. This exclusion also gets registered globally which disables trust checking for any code running in the same JVM."""


def test_advisory_basic():
    adv = AdvisoryRecord(
        cve_id="CVE-2015-5612",
        references=[
            "https://github.com/abc/def/commit/af542817cb325173410876aa3",
            "https://github.com/abc/def/issues/54",
        ],
    )
    assert adv.cve_id == "CVE-2015-5612"
    assert "https://github.com/abc/def/issues/54" in adv.references


def test_get_advisory():
    advisory = AdvisoryRecord("CVE-2021-22696")
    advisory.get_advisory()
    print(advisory.versions)
    assert advisory.cve_id == "CVE-2021-22696"
    # assert "3.4.0" in advisory.versions["affected"]
    # assert "3.4.3" in advisory.versions["fixed"]
    assert "3.4.3" in advisory.versions["lessThan"]


def test_build_advisory_record():
    advisory = build_advisory_record("CVE-2020-1925")
    print(advisory.references)
    # raise Exception("")
    assert advisory.cve_id == "CVE-2020-1925"


def test_debian_adv_lookup():
    pass
    # adv = AdvisoryRecord("CVE-2019-12419")
    # r = adv.search_references_debian_sec_tracker()
    # print(r)
    # raise Exception("")
