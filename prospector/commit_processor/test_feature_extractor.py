import pytest

# from datamodel import advisory
from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from git.git import Git

from .feature_extractor import (
    extract_avg_hunk_size,
    extract_changes_relevant_path,
    extract_contains_jira_reference,
    extract_features,
    extract_is_close_to_advisory_date,
    extract_n_changed_files,
    extract_n_hunks,
    extract_other_CVE_in_message,
    extract_references_ghissue,
    extract_references_vuln_id,
    extract_referred_to_by_advisories,
    extract_time_between_commit_and_advisory_record,
    is_commit_in_given_interval,
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
        description="Sample description for testing purposes. Intentionally referes to commit 7532d2f.",
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
    assert extracted_features.referred_to_by_advisories


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


def test_extract_avg_hunk_size():
    assert extract_avg_hunk_size([(3, 6)]) == 3
    assert extract_avg_hunk_size([(1, 3), (6, 11)]) == 3.5


def test_extract_n_hunks():
    assert extract_n_hunks(12) == 12


def test_extract_references_ghissue():
    assert extract_references_ghissue(["#12"])
    assert not extract_references_ghissue([])


def test_extract_n_changed_files():
    assert extract_n_changed_files(["a.java", "b.py", "c.php"]) == 3


def test_extract_contains_jira_reference():
    assert extract_contains_jira_reference(["NAME-213"])
    assert not extract_contains_jira_reference([])


def test_extract_referred_to_by_advisories(repository):
    commit = Commit(
        commit_id="r97993e3d78e1f5389b7b172ba9f308440830ce5",
        repository="test_repository",
    )
    advisory_record = AdvisoryRecord(vulnerability_id="CVE-2020-26258")
    assert extract_referred_to_by_advisories(
        commit, advisory_record, "http://127.0.0.1:8000"
    )
    commit = Commit(
        commit_id="f4d2eabd921cbd8808b9d923ee63d44538b4154f",
        repository="test_repository",
    )
    assert not extract_referred_to_by_advisories(
        commit, advisory_record, "http://127.0.0.1:8000"
    )
