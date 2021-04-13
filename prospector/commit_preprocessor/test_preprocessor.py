import pytest

from git.git import Git

from .preprocessor import extract_cve_references, preprocess_commit


@pytest.fixture
def repository():
    repo = Git("https://github.com/apache/struts")
    repo.clone()
    return repo


def test_proprocess_commit(repository):

    repo = repository
    commit = repo.get_commit("93f378809cc73c65c1d689a0e32ec440c52e7ce2")

    preprocessed_commit = preprocess_commit(commit)

    assert preprocessed_commit.log_msg.startswith(
        "Merge pull request #480 from apache/WW-5117-reorders-stack [WW-5117]"
    )

    assert preprocessed_commit.jira_refs == ["WW-5117"]
    assert preprocessed_commit.ghissue_refs == ["#480"]
    assert preprocessed_commit.cve_refs == []


def test_proprocess_commit_set(repository):

    repo = repository
    commit_set = repo.get_commits(
        since="1615441712", until="1617441712", filter_files="*.java"
    )
    preprocessed_commits = []

    for commit_id in commit_set:
        commit = repo.get_commit(commit_id)
        preprocessed_commits.append(preprocess_commit(commit))

    assert len(preprocessed_commits) == len(commit_set)


def test_extract_cve_identifiers():
    result = extract_cve_references(
        "bla bla bla CVE-1234-1234567 and CVE-1234-1234, fsafasf"
    )
    assert result == ["CVE-1234-1234567", "CVE-1234-1234"]
