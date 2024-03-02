import os.path
import time

import pytest

from git.git import Exec, Git

NEBULA = "https://github.com/slackhq/nebula"
BEAM = "https://github.com/apache/beam"
OPENCAST = "https://github.com/opencast/opencast"
OPENCAST_COMMIT = "bbb473f34ab95497d6c432c81285efb0c739f317"


COMMIT_ID = "4645e6034b9c88311856ee91d19b7328bd5878c1"
COMMIT_ID_1 = "d85e24f49f9efdeed5549a7d0874e68155e25301"
COMMIT_ID_2 = "b38bd36766994715ac5226bfa361cd2f8f29e31e"
COMMIT_ID_3 = "ae3ee42469b7c48848d841386ca9c74b7d6bbcd8"


@pytest.fixture
def repository() -> Git:
    repo = Git(OPENCAST)  # apache/beam
    repo.clone()
    return repo


def test_extract_timestamp(repository: Git):
    commit = repository.get_commit(OPENCAST_COMMIT)
    commit.extract_timestamp(format_date=True)
    assert commit.get_timestamp() == "2020-01-16 22:34:35"
    commit.extract_timestamp(format_date=False)
    assert commit.get_timestamp() == 1579214075


def test_show_tags(repository: Git):
    tags = repository.execute("git name-rev --tags")
    assert tags is not None


def test_get_tags_for_commit(repository: Git):
    commits = repository.create_commits()
    commit = commits.get(OPENCAST_COMMIT)
    if commit is not None:
        tags = commit.find_tags()
        # assert len(tags) == 75
        assert "10.2" in tags and "11.3" in tags and "9.4" in tags


def test_create_commits(repository: Git):
    commits = repository.create_commits()
    commit = commits.get(OPENCAST_COMMIT)
    assert commit.get_id() == OPENCAST_COMMIT


def test_get_hunks_count(repository: Git):
    commits = repository.create_commits()
    commit = commits.get(OPENCAST_COMMIT)
    _, hunks = commit.get_diff()
    assert hunks == 7


def test_get_changed_files(repository: Git):
    commit = repository.get_commit(OPENCAST_COMMIT)

    changed_files = commit.get_changed_files()
    assert len(changed_files) == 0


def test_run_cache():
    _exec = Exec(workdir=os.path.abspath("."))
    start = time.time_ns()
    for _ in range(1000):
        result = _exec.run("echo 42", cache=False)
        assert result == ["42"]
    no_cache_time = time.time_ns() - start

    _exec = Exec(workdir=os.path.abspath("."))
    start = time.time_ns()
    for _ in range(1000):
        result = _exec.run("echo 42", cache=True)
        assert result == ["42"]
    cache_time = time.time_ns() - start

    assert cache_time < no_cache_time
