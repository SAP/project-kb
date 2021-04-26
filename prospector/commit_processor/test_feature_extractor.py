import pytest

# from datamodel import advisory
from datamodel.advisory import AdvisoryRecord
from git.git import Git

from .feature_extractor import (
    extract_avg_hunk_size,
    extract_changes_relevant_path,
    extract_features,
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
    assert extracted_features.avg_hunk_size == 2


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


def test_extract_avg_hunk_size():
    assert extract_avg_hunk_size([(3, 6)]) == 3
    assert extract_avg_hunk_size([(1, 3), (6, 11)]) == 3.5
