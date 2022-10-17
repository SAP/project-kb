# from pprint import pprint
import os.path
import time

import pytest

from .git import Exec, Git

# from .version_to_tag import version_to_wide_interval_tags
from .version_to_tag import get_tag_for_version


REPO_URL = "https://github.com/slackhq/nebula"
COMMIT_ID = "b38bd36766994715ac5226bfa361cd2f8f29e31e"


@pytest.fixture
def repository() -> Git:
    repo = Git(REPO_URL)
    repo.clone()
    return repo


def test_extract_timestamp(repository: Git):
    commit = repository.get_commit(COMMIT_ID)
    commit.extract_timestamp(format_date=True)
    assert commit.get_timestamp() == "2022-04-04 17:38:36"
    commit.extract_timestamp(format_date=False)
    assert commit.get_timestamp() == 1649093916


def test_get_diff(repository: Git):
    commit = repository.get_commit(COMMIT_ID)
    diff = commit.get_diff()
    res = [s for s in diff if "connection_manager.go" in s]
    assert len(diff) == 16
    assert len(res) > 0


def test_get_changed_files(repository: Git):
    commit = repository.get_commit(COMMIT_ID)

    changed_files = commit.get_changed_files()
    assert len(changed_files) == 1
    assert "connection_manager.go" == changed_files[0]


# --------------------------------------------------------- #
# --------------------------------------------------------- #
# --------------------------------------------------------- #
# --------------------------------------------------------- #


def test_get_commits_in_time_interval():
    repo = Git(REPO_URL)
    repo.clone()

    results = repo.get_commits(since="1615441712", until="1617441712")
    assert len(results) == 42


@pytest.mark.skip(reason="Not working properly")
def test_extract_timestamp_from_version():
    repo = Git(REPO_URL)
    repo.clone()
    assert repo.extract_timestamp_from_version("v1.5.2") == 1639518536
    assert repo.extract_timestamp_from_version("INVALID_VERSION_1_0_0") is None


def test_get_tag_for_version():
    repo = Git(REPO_URL)
    repo.clone()
    tags = repo.get_tags()
    assert get_tag_for_version(tags, "1.5.2") == ["v1.5.2"]


# def test_legacy_mapping_version_to_tag_1():
#     repo = Git(REPO_URL)
#     repo.clone()

#     result = version_to_wide_interval_tags("2.3.34", repo)

#     assert result == [
#         ("STRUTS_2_3_33", "STRUTS_2_3_34"),
#         ("STRUTS_2_3_34", "STRUTS_2_3_35"),
#     ]


# def test_legacy_mapping_version_to_tag_2():
#     repo = Git(REPO_URL)
#     repo.clone()

#     result = version_to_wide_interval_tags("2.3.3", repo)

# assert result == [
#     ("STRUTS_2_3_2", "STRUTS_2_3_3"),
#     ("STRUTS_2_3_3", "STRUTS_2_3_4"),
# ]


def test_get_commit_parent():
    repo = Git(REPO_URL)
    repo.clone()
    id = repo.get_commit_id_for_tag("v1.6.1")
    commit = repo.get_commit(id)

    commit.get_parent_id()
    assert commit.parent_id == "4c0ae3df5ef79482134b1c08570ff51e52fdfe06"


def test_run_cache():
    _exec = Exec(workdir=os.path.abspath("."))
    start = time.time_ns()
    for _ in range(1000):
        result = _exec.run("echo 42", cache=False)
        assert result == ("42",)
    no_cache_time = time.time_ns() - start

    _exec = Exec(workdir=os.path.abspath("."))
    start = time.time_ns()
    for _ in range(1000):
        result = _exec.run("echo 42", cache=True)
        assert result == ("42",)
    cache_time = time.time_ns() - start

    assert cache_time < no_cache_time
