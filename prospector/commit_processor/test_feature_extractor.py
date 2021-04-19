import pytest

# from datamodel import advisory
from datamodel.advisory import AdvisoryRecord
from git.git import Git

from .feature_extractor import (
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
    )

    extracted_features = extract_features(processed_commit, advisory_record)

    assert extracted_features.references_vuln_id
    assert extracted_features.time_between_commit_and_advisory_record == 1000000


def test_extract_references_vuln_id():
    cve_ids = ["CVE-2020-26258", "CVE-1234-1234"]
    result = extract_references_vuln_id(cve_ids, "CVE-2020-26258")
    assert result


def test_time_between_commit_and_advisory_record():
    assert extract_time_between_commit_and_advisory_record(142, 100) == 42
