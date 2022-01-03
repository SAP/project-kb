import os

import pandas as pd
import pytest

from datamodel.commit import Commit

# from datamodel.commit_features import CommitWithFeatures
from filtering.filter import filter_commits

# from .config import *
from ranking import make_dataframe, predict, rank, train


@pytest.fixture
def candidates():
    return [
        Commit(repository="repo1", commit_id="1", ghissue_refs={"example": ""}),
        Commit(repository="repo2", commit_id="2"),
        Commit(repository="repo3", commit_id="3", ghissue_refs={"example": ""}),
        Commit(repository="repo4", commit_id="4"),
        Commit(repository="repo5", commit_id="5"),
    ]


def test_filter(candidates):
    result = filter_commits(candidates)
    assert isinstance(result, tuple)


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
