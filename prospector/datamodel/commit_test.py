# from dataclasses import asdict
from telnetlib import COM_PORT_OPTION
import pytest

from git.git import Git

from .commit import make_from_raw_commit


@pytest.fixture
def repository():
    repo = Git("https://github.com/slackhq/nebula")
    repo.clone()
    return repo


def test_preprocess_commit(repository: Git):

    repo = repository
    raw_commit = repo.get_commit("e434ba6523c4d6d22625755f9890039728e6676a")

    commit = make_from_raw_commit(raw_commit)

    assert commit.message.startswith("fix unsafe routes darwin (#610)")

    assert "610" in commit.ghissue_refs.keys()
    assert commit.cve_refs == []


def test_preprocess_commit_set(repository: Git):

    repo = repository
    commit_set = repo.get_commits(
        since="1615441712", until="1617441712", filter_files="go"
    )
    preprocessed_commits = []

    for commit_id in commit_set:
        raw_commit = repo.get_commit(commit_id)
        preprocessed_commits.append(make_from_raw_commit(raw_commit))

    assert len(preprocessed_commits) == len(commit_set)


def test_commit_ordering(repository: Git):
    assert True


def test_find_twin(repository: Git):
    assert True
