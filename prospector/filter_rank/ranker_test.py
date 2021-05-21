import os

import pandas as pd
import pytest

from datamodel.commit import Commit
from datamodel.commit_features import CommitFeatures
from filter_rank.ranker import (
    apply_rules,
    filter_commits,
    make_dataframe,
    predict,
    rank,
    train,
)


@pytest.fixture
def candidates():
    return [
        CommitFeatures(
            commit=Commit(repository="repo1", commit_id="1"),
            references_vuln_id=True,
            references_ghissue=True,
            changes_relevant_path=True,
        ),
        CommitFeatures(
            commit=Commit(repository="repo2", commit_id="2"),
            references_vuln_id=True,
            references_ghissue=False,
            changes_relevant_path=False,
        ),
        CommitFeatures(
            commit=Commit(repository="repo3", commit_id="3"),
            references_vuln_id=False,
            references_ghissue=True,
            changes_relevant_path=False,
        ),
        CommitFeatures(
            commit=Commit(repository="repo4", commit_id="4"),
            references_vuln_id=False,
            references_ghissue=False,
            changes_relevant_path=True,
        ),
        CommitFeatures(
            commit=Commit(repository="repo5", commit_id="5"),
            references_vuln_id=False,
            references_ghissue=False,
            changes_relevant_path=False,
        ),
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


def test_apply_rules(candidates):
    rules_filtered = apply_rules(candidates=candidates)
    assert candidates[0] in rules_filtered["Vuln ID is mentioned"]
    assert candidates[0] in rules_filtered["GitHub issue is mentioned"]
    assert candidates[0] in rules_filtered["Relevant path has been changed"]

    assert candidates[1] in rules_filtered["Vuln ID is mentioned"]
    assert candidates[1] not in rules_filtered["GitHub issue is mentioned"]
    assert candidates[1] not in rules_filtered["Relevant path has been changed"]

    assert candidates[2] not in rules_filtered["Vuln ID is mentioned"]
    assert candidates[2] in rules_filtered["GitHub issue is mentioned"]
    assert candidates[2] not in rules_filtered["Relevant path has been changed"]

    assert candidates[3] not in rules_filtered["Vuln ID is mentioned"]
    assert candidates[3] not in rules_filtered["GitHub issue is mentioned"]
    assert candidates[3] in rules_filtered["Relevant path has been changed"]

    assert candidates[4] not in rules_filtered["Vuln ID is mentioned"]
    assert candidates[4] not in rules_filtered["GitHub issue is mentioned"]
    assert candidates[4] not in rules_filtered["Relevant path has been changed"]
