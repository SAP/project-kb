from git.exec import Exec
from git.raw_commit import RawCommit
import pytest


@pytest.mark.skip(reason="It works of my machine")
def test_get_timestamp():
    commit = RawCommit(
        "https://github.com/slackhq/nebula",
        "b38bd36766994715ac5226bfa361cd2f8f29e31e",
        Exec(workdir="/tmp/gitcache/github.com_slackhq_nebula"),
    )
    assert commit.get_timestamp(format_date=True) == "2022-04-04 17:38:36"
    assert commit.get_timestamp(format_date=False) == 1649093916
