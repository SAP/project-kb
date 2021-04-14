import pytest

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit

from filter_rank.ranker import filter, rank


@pytest.fixture
def candidates():
    return [
        Commit("repo", "423423423"),
        Commit("repo", "423423423"),
        Commit("repo", "423423423"),
        Commit("repo", "423423423"),
    ]


def test_filter(candidates):
    ar = AdvisoryRecord("CVE-xxxx-yyyy")
    result = filter(ar, candidates)


def test_rank(candidates):
    ar = AdvisoryRecord("CVE-xxxx-yyyy")
    result = rank(ar, candidates)
