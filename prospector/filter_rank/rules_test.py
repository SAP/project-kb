import pytest

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.commit_features import CommitWithFeatures
from filter_rank.rules import apply_rules


@pytest.fixture
def candidates():
    return [
        CommitWithFeatures(
            commit=Commit(
                repository="repo1",
                commit_id="1",
                ghissue_refs=["example"],
                changed_files={"foo/bar/otherthing.xml", "pom.xml"},
            ),
            references_vuln_id=True,
        ),
        CommitWithFeatures(
            commit=Commit(repository="repo2", commit_id="2"),
            references_vuln_id=True,
            references_ghissue=False,
        ),
        CommitWithFeatures(
            commit=Commit(repository="repo3", commit_id="3", ghissue_refs=["example"]),
            references_vuln_id=False,
        ),
        CommitWithFeatures(
            commit=Commit(
                repository="repo4",
                commit_id="4",
                message="Endless loop causes DoS vulnerability",
                changed_files={"foo/bar/otherthing.xml", "pom.xml"},
            ),
            references_vuln_id=False,
            references_ghissue=False,
        ),
        CommitWithFeatures(
            commit=Commit(
                repository="repo5",
                commit_id="5",
                message="Insecure deserialization",
                changed_files={
                    "core/src/main/java/org/apache/cxf/workqueue/AutomaticWorkQueueImpl.java"
                },
            ),
            references_vuln_id=False,
            references_ghissue=False,
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
        code_tokens=["AutomaticWorkQueueImpl"],
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
    assert "SEC_KEYWORD_IN_COMMIT_MSG" in annotated_candidates[3].annotations

    assert "SEC_KEYWORD_IN_COMMIT_MSG" in annotated_candidates[4].annotations
    assert "TOKENS_IN_MODIFIED_PATHS" in annotated_candidates[4].annotations
