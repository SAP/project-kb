import pytest

# from datamodel import advisory
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from git.git import Git

from .feature_extractor import (
    extract_changes_relevant_path,
    extract_features,
    extract_is_close_to_advisory_date,
    extract_other_CVE_in_message,
    extract_references_vuln_id,
    extract_referred_to_by_nvd,
    extract_time_between_commit_and_advisory_record,
    is_commit_in_given_interval,
)
from .preprocessor import preprocess_commit

cve_cached_response = {
    "cve": {
        "data_type": "CVE",
        "data_format": "MITRE",
        "data_version": "4.0",
        "CVE_data_meta": {
            "ID": "CVE-2020-26258",
            "ASSIGNER": "security-advisories@github.com",
        },
        "problemtype": {
            "problemtype_data": [{"description": [{"lang": "en", "value": "CWE-918"}]}]
        },
        "references": {
            "reference_data": [
                {
                    "url": "https://github.com/x-stream/xstream/security/advisories/GHSA-4cch-wxpw-8p28",
                    "name": "https://github.com/x-stream/xstream/security/advisories/GHSA-4cch-wxpw-8p28",
                    "refsource": "CONFIRM",
                    "tags": ["Mitigation", "Third Party Advisory"],
                },
                {
                    "url": "https://x-stream.github.io/CVE-2020-26258.html",
                    "name": "https://x-stream.github.io/CVE-2020-26258.html",
                    "refsource": "MISC",
                    "tags": ["Exploit", "Mitigation", "Third Party Advisory"],
                },
                {
                    "url": "https://lists.apache.org/thread.html/r97993e3d78e1f5389b7b172ba9f308440830ce5f051ee62714a0aa34@%3Ccommits.struts.apache.org%3E",
                    "name": "[struts-commits] 20201221 [struts] branch master updated: Upgrades XStream to version 1.4.15 to address CVE-2020-26258, CVE-2020-26259",
                    "refsource": "MLIST",
                    "tags": ["Mailing List", "Third Party Advisory"],
                },
                {
                    "url": "https://lists.debian.org/debian-lts-announce/2020/12/msg00042.html",
                    "name": "[debian-lts-announce] 20201231 [SECURITY] [DLA 2507-1] libxstream-java security update",
                    "refsource": "MLIST",
                    "tags": ["Mailing List", "Third Party Advisory"],
                },
                {
                    "url": "https://www.debian.org/security/2021/dsa-4828",
                    "name": "DSA-4828",
                    "refsource": "DEBIAN",
                    "tags": ["Third Party Advisory"],
                },
                {
                    "url": "https://security.netapp.com/advisory/ntap-20210409-0005/",
                    "name": "https://security.netapp.com/advisory/ntap-20210409-0005/",
                    "refsource": "CONFIRM",
                    "tags": ["Third Party Advisory"],
                },
            ]
        },
        "description": {
            "description_data": [
                {
                    "lang": "en",
                    "value": "XStream is a Java library to serialize objects to XML and back again. In XStream before version 1.4.15, a Server-Side Forgery Request vulnerability can be activated when unmarshalling. The vulnerability may allow a remote attacker to request data from internal resources that are not publicly available only by manipulating the processed input stream. If you rely on XStream's default blacklist of the Security Framework, you will have to use at least version 1.4.15. The reported vulnerability does not exist if running Java 15 or higher. No user is affected who followed the recommendation to setup XStream's Security Framework with a whitelist! Anyone relying on XStream's default blacklist can immediately switch to a whilelist for the allowed types to avoid the vulnerability. Users of XStream 1.4.14 or below who still want to use XStream default blacklist can use a workaround described in more detailed in the referenced advisories.",
                }
            ]
        },
    },
    "configurations": {
        "CVE_data_version": "4.0",
        "nodes": [
            {
                "operator": "OR",
                "children": [],
                "cpe_match": [
                    {
                        "vulnerable": True,
                        "cpe23Uri": "cpe:2.3:a:xstream_project:xstream:*:*:*:*:*:*:*:*",
                        "versionEndExcluding": "1.4.15",
                        "cpe_name": [],
                    }
                ],
            },
            {
                "operator": "OR",
                "children": [],
                "cpe_match": [
                    {
                        "vulnerable": True,
                        "cpe23Uri": "cpe:2.3:o:debian:debian_linux:9.0:*:*:*:*:*:*:*",
                        "cpe_name": [],
                    },
                    {
                        "vulnerable": True,
                        "cpe23Uri": "cpe:2.3:o:debian:debian_linux:10.0:*:*:*:*:*:*:*",
                        "cpe_name": [],
                    },
                ],
            },
        ],
    },
    "impact": {
        "baseMetricV3": {
            "cvssV3": {
                "version": "3.1",
                "vectorString": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N",
                "attackVector": "NETWORK",
                "attackComplexity": "LOW",
                "privilegesRequired": "LOW",
                "userInteraction": "NONE",
                "scope": "CHANGED",
                "confidentialityImpact": "HIGH",
                "integrityImpact": "NONE",
                "availabilityImpact": "NONE",
                "baseScore": 7.7,
                "baseSeverity": "HIGH",
            },
            "exploitabilityScore": 3.1,
            "impactScore": 4,
        },
        "baseMetricV2": {
            "cvssV2": {
                "version": "2.0",
                "vectorString": "AV:N/AC:L/Au:N/C:P/I:N/A:N",
                "accessVector": "NETWORK",
                "accessComplexity": "LOW",
                "authentication": "NONE",
                "confidentialityImpact": "PARTIAL",
                "integrityImpact": "NONE",
                "availabilityImpact": "NONE",
                "baseScore": 5,
            },
            "severity": "MEDIUM",
            "exploitabilityScore": 10,
            "impactScore": 2.9,
            "acInsufInfo": False,
            "obtainAllPrivilege": False,
            "obtainUserPrivilege": False,
            "obtainOtherPrivilege": False,
            "userInteractionRequired": False,
        },
    },
    "publishedDate": "2020-12-16T01:15Z",
    "lastModifiedDate": "2021-04-13T18:14Z",
}


@pytest.fixture
def repository():
    repo = Git("https://github.com/apache/struts")
    repo.clone()
    return repo


def test_extract_features(repository, requests_mock):
    requests_mock.get(
        "http://127.0.0.1:8000/nvd/vulnerabilities/CVE-2020-26258",
        json=cve_cached_response,
    )

    repo = repository
    commit = repo.get_commit("7532d2fb0d6081a12c2a48ec854a81a8b718be62")
    processed_commit = preprocess_commit(commit)

    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        repository_url="https://github.com/apache/struts",
        published_timestamp=1607532756,
        paths=["pom.xml"],
    )

    extracted_features = extract_features(processed_commit, advisory_record)

    assert extracted_features.references_vuln_id
    assert extracted_features.time_between_commit_and_advisory_record == 1000000
    assert extracted_features.changes_relevant_path
    assert not extracted_features.other_CVE_in_message
    assert (
        extracted_features.commit_falls_in_given_interval_based_on_advisory_publicatation_date
    )
    assert extracted_features.avg_hunk_size == 2
    assert extracted_features.n_hunks == 1
    assert not extracted_features.references_ghissue
    assert extracted_features.n_changed_files == 1
    assert extracted_features.contains_jira_reference
    assert not extracted_features.referred_to_by_nvd


def test_extract_references_vuln_id():
    commit = Commit(
        commit_id="test_commit",
        repository="test_repository",
        cve_refs=["test_advisory_record", "another_advisory_record"],
    )
    advisory_record = AdvisoryRecord(vulnerability_id="test_advisory_record")
    result = extract_references_vuln_id(commit, advisory_record)
    assert result


def test_time_between_commit_and_advisory_record():
    commit = Commit(
        commit_id="test_commit", repository="test_repository", timestamp=142
    )
    advisory_record = AdvisoryRecord(
        vulnerability_id="test_advisory_record", published_timestamp=100
    )
    assert (
        extract_time_between_commit_and_advisory_record(commit, advisory_record) == 42
    )


def test_extract_changes_relevant_path():
    path_1 = "a/b.py"
    path_2 = "a/c.py"
    path_3 = "a/d.py"

    commit = Commit(
        commit_id="test_commit", repository="test_repository", changed_files=[path_1]
    )
    advisory_record = AdvisoryRecord(
        vulnerability_id="test_advisory_record", paths=[path_1, path_2]
    )
    assert extract_changes_relevant_path(commit, advisory_record)

    commit = Commit(
        commit_id="test_commit",
        repository="test_repository",
        changed_files=[path_1, path_2],
    )
    advisory_record = AdvisoryRecord(
        vulnerability_id="test_advisory_record", paths=[path_2]
    )
    assert extract_changes_relevant_path(commit, advisory_record)

    commit = Commit(
        commit_id="test_commit", repository="test_repository", changed_files=[path_3]
    )
    advisory_record = AdvisoryRecord(
        vulnerability_id="test_advisory_record", paths=[path_1, path_2]
    )
    assert not extract_changes_relevant_path(commit, advisory_record)

    commit = Commit(
        commit_id="test_commit",
        repository="test_repository",
        changed_files=[path_1, path_2],
    )
    advisory_record = AdvisoryRecord(
        vulnerability_id="test_advisory_record", paths=[path_3]
    )
    assert not extract_changes_relevant_path(commit, advisory_record)

    commit = Commit(
        commit_id="test_commit", repository="test_repository", changed_files=[]
    )
    advisory_record = AdvisoryRecord(
        vulnerability_id="test_advisory_record", paths=[path_1, path_2]
    )
    assert not extract_changes_relevant_path(commit, advisory_record)

    commit = Commit(
        commit_id="test_commit",
        repository="test_repository",
        changed_files=[path_1, path_2],
    )
    advisory_record = AdvisoryRecord(vulnerability_id="test_advisory_record", paths=[])
    assert not extract_changes_relevant_path(commit, advisory_record)


def test_extract_other_CVE_in_message():
    commit = Commit(
        commit_id="test_commit",
        repository="test_repository",
        cve_refs=["CVE-2021-29425", "CVE-2021-21251"],
    )
    advisory_record = AdvisoryRecord(vulnerability_id="CVE-2020-31284")
    assert extract_other_CVE_in_message(commit, advisory_record)
    advisory_record = AdvisoryRecord(vulnerability_id="CVE-2021-29425")
    assert not extract_other_CVE_in_message(commit, advisory_record)


def test_is_commit_in_given_interval():
    assert is_commit_in_given_interval(1359961896, 1359961896, 0)
    assert is_commit_in_given_interval(1359961896, 1360047896, 1)
    assert is_commit_in_given_interval(1359961896, 1359875896, -1)
    assert not is_commit_in_given_interval(1359961896, 1359871896, -1)
    assert not is_commit_in_given_interval(1359961896, 1360051896, 1)


def test_extract_is_close_to_advisory_date(
    repository,
):

    repo = repository
    commit = repo.get_commit("7532d2fb0d6081a12c2a48ec854a81a8b718be62")
    test_commit = preprocess_commit(commit)

    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        repository_url="https://github.com/apache/struts",
        paths=["pom.xml"],
        published_timestamp=1000000,
        versions=["STRUTS_2_1_3", "STRUTS_2_3_9"],
    )

    test_commit.timestamp = 1000000
    assert extract_is_close_to_advisory_date(test_commit, advisory_record, 1, 1)

    test_commit.timestamp = 1086401
    assert not extract_is_close_to_advisory_date(test_commit, advisory_record, 1, 1)

    test_commit.timestamp = 913598
    assert not extract_is_close_to_advisory_date(test_commit, advisory_record, 1, 1)

    test_commit.timestamp = 1000000
    assert extract_is_close_to_advisory_date(test_commit, advisory_record, 0, 0)

    test_commit.timestamp = 1000001
    assert not extract_is_close_to_advisory_date(test_commit, advisory_record, 0, 0)

    test_commit.timestamp = 1086398
    assert extract_is_close_to_advisory_date(test_commit, advisory_record, 0, 1)

    test_commit.timestamp = 1086401
    assert not extract_is_close_to_advisory_date(test_commit, advisory_record, 0, 1)

    test_commit.timestamp = 913598
    assert not extract_is_close_to_advisory_date(test_commit, advisory_record, 1, 0)

    test_commit.timestamp = 913601
    assert extract_is_close_to_advisory_date(test_commit, advisory_record, 1, 0)


def test_extract_referred_to_by_nvd(repository, requests_mock):
    requests_mock.get(
        "http://127.0.0.1:8000/nvd/vulnerabilities/CVE-2020-26258",
        json=cve_cached_response,
    )

    advisory_record = AdvisoryRecord(vulnerability_id="CVE-2020-26258")

    commit = Commit(
        commit_id="r97993e3d78e1f5389b7b172ba9f308440830ce5",
        repository="test_repository",
    )
    assert extract_referred_to_by_nvd(commit, advisory_record, "http://127.0.0.1:8000")

    commit = Commit(
        commit_id="f4d2eabd921cbd8808b9d923ee63d44538b4154f",
        repository="test_repository",
    )
    assert not extract_referred_to_by_nvd(
        commit, advisory_record, "http://127.0.0.1:8000"
    )
