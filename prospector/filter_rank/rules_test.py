import pytest

from datamodel.commit import Commit
from datamodel.commit_features import CommitWithFeatures
from filter_rank.rules import apply_rules


@pytest.fixture
def candidates():
    return [
        CommitWithFeatures(
            commit=Commit(repository="repo1", commit_id="1", ghissue_refs=["example"]),
            references_vuln_id=True,
            # references_ghissue=True,
            changes_relevant_path=True,
        ),
        CommitWithFeatures(
            commit=Commit(repository="repo2", commit_id="2"),
            references_vuln_id=True,
            references_ghissue=False,
            changes_relevant_path=False,
        ),
        CommitWithFeatures(
            commit=Commit(repository="repo3", commit_id="3", ghissue_refs=["example"]),
            references_vuln_id=False,
            # references_ghissue=True,
            changes_relevant_path=False,
        ),
        CommitWithFeatures(
            commit=Commit(repository="repo4", commit_id="4"),
            references_vuln_id=False,
            references_ghissue=False,
            changes_relevant_path=True,
        ),
        CommitWithFeatures(
            commit=Commit(repository="repo5", commit_id="5"),
            references_vuln_id=False,
            references_ghissue=False,
            changes_relevant_path=False,
        ),
    ]


def test_apply_rules(candidates: "list[CommitWithFeatures]"):
    print(type(candidates))
    annotated_candidates = apply_rules(candidates=candidates)
    print(annotated_candidates)
    print(type(annotated_candidates))

    assert len(annotated_candidates[0].annotations) > 0
    assert "Vuln ID is mentioned" in annotated_candidates[0].annotations
    assert "GitHub issue is mentioned" in annotated_candidates[0].annotations
    assert "Relevant path has been changed" in annotated_candidates[0].annotations

    assert len(annotated_candidates[1].annotations) > 0
    assert "Vuln ID is mentioned" in annotated_candidates[1].annotations
    assert "GitHub issue is mentioned" not in annotated_candidates[1].annotations
    assert "Relevant path has been changed" not in annotated_candidates[1].annotations

    assert len(annotated_candidates[2].annotations) > 0
    assert "Vuln ID is mentioned" not in annotated_candidates[2].annotations
    assert "GitHub issue is mentioned" in annotated_candidates[2].annotations
    assert "Relevant path has been changed" not in annotated_candidates[2].annotations

    assert len(annotated_candidates[3].annotations) > 0
    assert "Vuln ID is mentioned" not in annotated_candidates[3].annotations
    assert "GitHub issue is mentioned" not in annotated_candidates[3].annotations
    assert "Relevant path has been changed" in annotated_candidates[3].annotations

    assert len(annotated_candidates[4].annotations) == 0
