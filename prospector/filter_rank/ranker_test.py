import pytest
import os
import pandas as pd

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit

from filter_rank.ranker import filter_commits, rank, train, _get_training_dataframe


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


def test_rank(candidates):
    ar = AdvisoryRecord("CVE-xxxx-yyyy")
    result = rank(ar, candidates)


def test_train():
    path = train("test123")
    assert os.path.exists(path)

    if os.path.exists(path):
        os.remove(path)


def test_get_training_dataframe():
    df = _get_training_dataframe()
    assert isinstance(df, pd.DataFrame)
