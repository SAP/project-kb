# from dataclasses import asdict
import time
from unittest import result

from pytest import skip
from datamodel.advisory import AdvisoryRecord, build_advisory_record
from .nlp import RELEVANT_EXTENSIONS

# import pytest


def test_advisory_basic():
    adv_rec = AdvisoryRecord(
        vulnerability_id="CVE-2015-5612",
        repository_url="https://github.com/abc/xyz",
        references=[
            "https://github.com/abc/def/commit/af542817cb325173410876aa3",
            "https://github.com/abc/def/issues/54",
        ],
    )

    assert adv_rec.repository_url == "https://github.com/abc/xyz"

    mentions_commit = False
    for r in adv_rec.references:
        if "af542817c" in r:
            mentions_commit = True

    assert mentions_commit
    # assert ar.vulnerability_id == "CVE-2015-5612"
    # assert ar.published_timestamp == "2015-09-04T15:59Z"


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


def test_adv_record_versions():

    record = AdvisoryRecord(vulnerability_id="CVE-2014-0050", description=ADVISORY_TEXT)
    record.analyze()

    assert "15.26.1" in record.versions
    assert "15.26" not in record.versions


# def test_adv_record_nvd():
#     record = AdvisoryRecord(vulnerability_id="CVE-2014-0050")

#     record.analyze(use_nvd=True)

#     # print(record)
#     assert "1.3.1" in record.versions
#     assert "1.3" not in record.versions


def test_adv_record_products():
    record = AdvisoryRecord(vulnerability_id="CVE-XXXX-YYYY", description=ADVISORY_TEXT)
    record.analyze()

    # print(record)
    assert "Chrysler" in record.affected_products


def test_adv_record_keywords():
    record = AdvisoryRecord(
        vulnerability_id="CVE-XXXX-YYYY", description=ADVISORY_TEXT_2
    )
    record.analyze()

    # TODO replace when NLP implementation is done
    # see, https://github.com/SAP/project-kb/issues/256#issuecomment-927639866
    assert record.keywords == () or sorted(record.keywords) == sorted(
        (
            "IO",
            "2.7,",
            "FileNameUtils.normalize",
            '"//../foo",',
            '"\\..\\foo",',
            '"limited"',
        )
    )


def test_build():
    record = build_advisory_record(
        "CVE-2014-0050", "", "", "", "", True, "", "", "", "*.java"
    )
    assert "MultipartStream" in record.paths
    assert record.vulnerability_id == "CVE-2014-0050"


@skip(reason="Slow connections make it fail")
def test_filenames_extraction():
    cve = {
        "CVE-2014-0050": "MultipartStream",
        "CVE-2021-22696": "JwtRequestCodeFilter",  # Should match JwtRequestCodeFilter
        "CVE-2021-27582": "OAuthConfirmationController",
        "CVE-2021-29425": "FileNameUtils",
        "CVE-2021-30468": "JsonMapObjectReaderWriter",
    }

    result1 = build_advisory_record(
        "CVE-2014-0050", "", "", "", "", True, "", "", "", ""
    )
    result2 = build_advisory_record(
        "CVE-2021-22696", "", "", "", "", True, "", "", "", ""
    )
    result3 = build_advisory_record(
        "CVE-2021-27582", "", "", "", "", True, "", "", "", ""
    )
    result4 = build_advisory_record(
        "CVE-2021-29425", "", "", "", "", True, "", "", "", ""
    )
    result5 = build_advisory_record(
        "CVE-2021-30468", "", "", "", "", True, "", "", "", ""
    )
    assert (
        result1.paths.sort() == ["MultiPartStream", "FileUpload"].sort()
    )  # Content-Type
    assert result2.paths.sort() == ["JwtRequestCodeFilter", "request_uri"].sort()
    assert (
        result3.paths.sort()
        == [
            "OAuthConfirmationController",
            "@ModelAttribute",
            "authorizationRequest",
        ].sort()
    )
    assert result4.paths.sort() == ["FileNameUtils"].sort()
    assert result5.paths.sort() == ["JsonMapObjectReaderWriter"].sort()

    # raise Exception("Test failed")


# def test_adv_record_project_data():
#     record = AdvisoryRecord(vulnerability_id="CVE-XXXX-YYYY", description=ADVISORY_TEXT_2)
#     record.analyze()

#     # print(record)
#     assert "Chrysler" in record.affected_products
