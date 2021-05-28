import os

import pandas as pd
import pytest

from datamodel.commit import Commit
from datamodel.commit_features import CommitFeatures
from filter_rank.filter import filter_commits
from filter_rank.rank import make_dataframe, predict, rank, train
from filter_rank.rules import apply_rules


@pytest.fixture
def candidates():
    return [
        CommitFeatures(
            commit=Commit(repository="repo1", commit_id="1", ghissue_refs=["example"]),
            references_vuln_id=True,
            # references_ghissue=True,
            changes_relevant_path=True,
        ),
        CommitFeatures(
            commit=Commit(repository="repo2", commit_id="2"),
            references_vuln_id=True,
            references_ghissue=False,
            changes_relevant_path=False,
        ),
        CommitFeatures(
            commit=Commit(repository="repo3", commit_id="3", ghissue_refs=["example"]),
            references_vuln_id=False,
            # references_ghissue=True,
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
    print(rules_filtered)
    assert candidates[0] in rules_filtered
    assert "Vuln ID is mentioned" in rules_filtered[candidates[0]]
    assert "GitHub issue is mentioned" in rules_filtered[candidates[0]]
    assert "Relevant path has been changed" in rules_filtered[candidates[0]]

    assert candidates[1] in rules_filtered
    assert "Vuln ID is mentioned" in rules_filtered[candidates[1]]
    assert "GitHub issue is mentioned" not in rules_filtered[candidates[1]]
    assert "Relevant path has been changed" not in rules_filtered[candidates[1]]

    assert candidates[2] in rules_filtered
    assert "Vuln ID is mentioned" not in rules_filtered[candidates[2]]
    assert "GitHub issue is mentioned" in rules_filtered[candidates[2]]
    assert "Relevant path has been changed" not in rules_filtered[candidates[2]]

    assert candidates[3] in rules_filtered
    assert "Vuln ID is mentioned" not in rules_filtered[candidates[3]]
    assert "GitHub issue is mentioned" not in rules_filtered[candidates[3]]
    assert "Relevant path has been changed" in rules_filtered[candidates[3]]

    assert candidates[4] not in rules_filtered
