import pytest

# from datamodel import advisory
from datamodel.advisory import AdvisoryRecord
from git.git import Git

from .feature_extractor import (
    extract_changes_relevant_path,
    extract_contains_jira_reference,
    extract_features,
    extract_n_changed_files,
    extract_n_hunks,
    extract_references_ghissue,
    extract_references_vuln_id,
    extract_time_between_commit_and_advisory_record,
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
    assert extracted_features.n_hunks == 1
    assert not extracted_features.references_ghissue
    assert extracted_features.n_changed_files == 1
    assert extracted_features.contains_jira_reference


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
