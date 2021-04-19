import pytest
import os
import pandas as pd

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit

from filter_rank.ranker import filter_commits, rank, train, make_dataframe


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
    result = filter_commits(ar, candidates)
    assert isinstance(result, list)


def test_rank(candidates):
    ar = AdvisoryRecord("CVE-xxxx-yyyy")
    result = rank(ar, candidates)
    assert isinstance(result, list)


def test_train():
    path = train("test123")
    assert os.path.exists(path)

    if os.path.exists(path):
        os.remove(path)


def test_get_training_dataframe():
    df = make_dataframe()
    assert isinstance(df, pd.DataFrame)
