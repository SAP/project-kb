import pytest

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.commit_features import CommitWithFeatures
from filter_rank.rules import apply_rules


@pytest.fixture
def candidates():
    return [
        CommitWithFeatures(
            commit=Commit(repository="repo1", commit_id="1", ghissue_refs=["example"]),
            references_vuln_id=True,
            # TODO: https://github.com/SAP/project-kb/issues/201
            # references_ghissue=True,
            changes_relevant_path={"foo/bar/otherthing.xml", "pom.xml"},
        ),
        CommitWithFeatures(
            commit=Commit(repository="repo2", commit_id="2"),
            references_vuln_id=True,
            # TODO: https://github.com/SAP/project-kb/issues/201
            # references_ghissue=False,
            changes_relevant_path=set(),
        ),
        CommitWithFeatures(
            commit=Commit(repository="repo3", commit_id="3", ghissue_refs=["example"]),
            references_vuln_id=False,
            # TODO: https://github.com/SAP/project-kb/issues/201
            # references_ghissue=True,
            changes_relevant_path=set(),
        ),
        CommitWithFeatures(
            commit=Commit(repository="repo4", commit_id="4"),
            references_vuln_id=False,
            # TODO: https://github.com/SAP/project-kb/issues/201
            # references_ghissue=False,
            changes_relevant_path={"foo/bar/otherthing.xml", "pom.xml"},
        ),
        CommitWithFeatures(
            commit=Commit(repository="repo5", commit_id="5"),
            references_vuln_id=False,
            # TODO: https://github.com/SAP/project-kb/issues/201
            # references_ghissue=False,
            changes_relevant_path=set(),
        ),
    ]


@pytest.fixture
def advisory_record():
    return AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        repository_url="https://github.com/apache/struts",
        published_timestamp=1607532756,
        references=[
            "https://reference.to/some/commit/7532d2fb0d6081a12c2a48ec854a81a8b718be62"
        ],
        paths=["pom.xml"],
    )


def test_apply_rules(
    candidates: "list[CommitWithFeatures]", advisory_record: AdvisoryRecord
):
    annotated_candidates = apply_rules(
        candidates=candidates, advisory_record=advisory_record
    )

    print(annotated_candidates[0].annotations)

    assert len(annotated_candidates[0].annotations) > 0
    assert "REF_ADV_VULN_ID" in annotated_candidates[0].annotations
    assert "REF_GH_ISSUE" in annotated_candidates[0].annotations
    assert "CH_REL_PATH" in annotated_candidates[0].annotations

    assert len(annotated_candidates[1].annotations) > 0
    assert "REF_ADV_VULN_ID" in annotated_candidates[1].annotations
    assert "REF_GH_ISSUE" not in annotated_candidates[1].annotations
    assert "CH_REL_PATH" not in annotated_candidates[1].annotations

    assert len(annotated_candidates[2].annotations) > 0
    assert "REF_ADV_VULN_ID" not in annotated_candidates[2].annotations
    assert "REF_GH_ISSUE" in annotated_candidates[2].annotations
    assert "CH_REL_PATH" not in annotated_candidates[2].annotations

    assert len(annotated_candidates[3].annotations) > 0
    assert "REF_ADV_VULN_ID" not in annotated_candidates[3].annotations
    assert "REF_GH_ISSUE" not in annotated_candidates[3].annotations
    assert "CH_REL_PATH" in annotated_candidates[3].annotations

    assert len(annotated_candidates[4].annotations) == 0
