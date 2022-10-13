# from dataclasses import asdict
import pytest

from git.git import Git

from .commit import make_from_raw_commit

SHENYU = "https://github.com/apache/shenyu"
COMMIT = "0e826ceae97a1258cb15c73a3072118c920e8654"
COMMIT_2 = "530bff5a0618062d3f253dab959785ce728d1f3c"


@pytest.fixture
def repository():
    repo = Git(SHENYU)  # Git("https://github.com/slackhq/nebula")
    repo.clone()
    return repo


def test_preprocess_commit(repository: Git):

    repo = repository
    raw_commit = repo.get_commit(
        COMMIT_2
    )  # repo.get_commit("e434ba6523c4d6d22625755f9890039728e6676a")

    make_from_raw_commit(raw_commit)


def test_preprocess_commit_set(repository: Git):

    repo = repository
    commit_set = repo.get_commits(since="1615441712", until="1617441712")
    preprocessed_commits = []

    for commit_id in commit_set:
        raw_commit = repo.get_commit(commit_id)
        preprocessed_commits.append(make_from_raw_commit(raw_commit))

    assert len(preprocessed_commits) == len(commit_set)


def test_commit_ordering(repository: Git):
    assert True


def test_find_twin(repository: Git):
    assert True
