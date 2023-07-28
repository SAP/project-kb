import pytest

from git.git import Git
from git.raw_commit import RawCommit

NEBULA = "https://github.com/slackhq/nebula"
BEAM = "https://github.com/apache/beam"
OPENCAST = "https://github.com/opencast/opencast"
OPENCAST_COMMIT = "bbb473f34ab95497d6c432c81285efb0c739f317"


COMMIT_ID = "4645e6034b9c88311856ee91d19b7328bd5878c1"
COMMIT_ID_1 = "d85e24f49f9efdeed5549a7d0874e68155e25301"
COMMIT_ID_2 = "b38bd36766994715ac5226bfa361cd2f8f29e31e"
COMMIT_ID_3 = "ae3ee42469b7c48848d841386ca9c74b7d6bbcd8"


@pytest.fixture
def commit():
    repository = Git(OPENCAST)
    repository.clone()
    commits = repository.create_commits()
    return commits.get(OPENCAST_COMMIT)


def test_find_tags(commit: RawCommit):
    tags = commit.find_tags()
    # assert len(tags) == 75
    assert "10.2" in tags and "11.3" in tags and "9.4" in tags


def test_get_diff(commit: RawCommit):
    diff, _ = commit.get_diff()
    assert diff is not None
