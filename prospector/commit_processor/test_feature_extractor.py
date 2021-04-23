import pytest

# from datamodel import advisory
from datamodel.advisory import AdvisoryRecord
from git.git import Git

from .feature_extractor import (
    extract_changes_relevant_path,
    extract_commit_falls_in_interval_based_on_advisory_publicatation_date,
    extract_commit_in_given_inverval,
    extract_commit_in_invertal,
    extract_features,
    extract_references_vuln_id,
    extract_time_between_commit_and_advisory_record,
    extract_timestamp_from_version,
)
from .preprocessor import preprocess_commit


@pytest.fixture
def repository():
    repo = Git("https://github.com/apache/struts")
    repo.clone()
    return repo


def test_extract_features(repository):

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


def test_extract_references_vuln_id():
    cve_ids = ["CVE-2020-26258", "CVE-1234-1234"]
    result = extract_references_vuln_id(cve_ids, "CVE-2020-26258")
    assert result


def test_time_between_commit_and_advisory_record():
    assert extract_time_between_commit_and_advisory_record(142, 100) == 42


def test_extract_changes_relevant_path():
    path_1 = "a/b.py"
    path_2 = "a/c.py"
    path_3 = "a/d.py"
    assert extract_changes_relevant_path(
        relevant_paths=[path_1], changed_paths=[path_1, path_2]
    )
    assert extract_changes_relevant_path(
        relevant_paths=[path_1, path_2], changed_paths=[path_2]
    )
    assert not extract_changes_relevant_path(
        relevant_paths=[path_3], changed_paths=[path_1, path_2]
    )
    assert not extract_changes_relevant_path(
        relevant_paths=[path_1, path_2], changed_paths=[path_3]
    )
    assert not extract_changes_relevant_path(
        relevant_paths=[], changed_paths=[path_1, path_2]
    )
    assert not extract_changes_relevant_path(
        relevant_paths=[path_1, path_2], changed_paths=[]
    )


def test_extract_timestamp_from_version(repository):
    repo = repository
    assert extract_timestamp_from_version("STRUTS_2_3_9", repo) == 1359961896
    assert extract_timestamp_from_version("INVALID_VERSION_1_0_0", repo) is None


def test_extract_commit_in_invertal():
    assert extract_commit_in_invertal(1359961896, 1359961897, 1359961896)
    assert extract_commit_in_invertal(1359961896, 1359961896, 1359961896)
    assert not extract_commit_in_invertal(1359961896, 1359961897, 1359961897)
    assert not extract_commit_in_invertal(1359961896, 1359961897, 1359961898)


def test_extract_commit_in_given_invertal():
    assert extract_commit_in_given_inverval(1359961896, 1359961896, 0)
    assert extract_commit_in_given_inverval(1359961896, 1360047896, 1)
    assert extract_commit_in_given_inverval(1359961896, 1359875896, -1)
    assert not extract_commit_in_given_inverval(1359961896, 1359871896, -1)
    assert not extract_commit_in_given_inverval(1359961896, 1360051896, 1)


def test_extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
    repository,
):

    advisory_record = AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        repository_url="https://github.com/apache/struts",
        paths=["pom.xml"],
        published_timestamp=1000000,
        versions=["STRUTS_2_1_3", "STRUTS_2_3_9"],
    )

    assert extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
        1000000, advisory_record, 1, 1
    )
    assert not extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
        1086401, advisory_record, 1, 1
    )
    assert not extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
        913598, advisory_record, 1, 1
    )
    assert extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
        1000000, advisory_record, 0, 0
    )
    assert not extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
        1000001, advisory_record, 0, 0
    )
    assert extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
        1086398, advisory_record, 0, 1
    )
    assert not extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
        1086401, advisory_record, 0, 1
    )
    assert not extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
        913598, advisory_record, 1, 0
    )
    assert extract_commit_falls_in_interval_based_on_advisory_publicatation_date(
        913601, advisory_record, 1, 0
    )
