import os

import pandas as pd
import pytest

from datamodel.commit import Commit
from datamodel.commit_features import CommitFeatures
from filter_rank.ranker import filter_commits, make_dataframe, predict, rank, train


@pytest.fixture
def candidates():
    return [
        CommitFeatures(commit=Commit(repository="repo", commit_id="423423423")),
        CommitFeatures(commit=Commit(repository="repo", commit_id="423423423")),
        CommitFeatures(commit=Commit(repository="repo", commit_id="423423423")),
        CommitFeatures(commit=Commit(repository="repo", commit_id="423423423")),
    ]


def test_filter(candidates):
    result = filter_commits(candidates)
    assert isinstance(result, list)


def test_rank(candidates):
    model_name = "LR_15_components"
    result = rank(candidates, model_name)
    assert isinstance(result, list)


def test_train():
    path = train("test123")
    assert os.path.exists(path)

    if os.path.exists(path):
        os.remove(path)


def test_get_training_dataframe():
    df = make_dataframe()
    assert isinstance(df, pd.DataFrame)


def test_predict(candidates):
    model_name = "LR_15_components"
    commit = candidates[0]
    score = predict(model_name, commit)
    assert isinstance(score, float)
