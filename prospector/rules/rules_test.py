from typing import List

import pytest

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from rules.rules import apply_rules

# from datamodel.commit_features import CommitWithFeatures


@pytest.fixture
def candidates():
    return [
        Commit(
            repository="repo1",
            commit_id="1",
            message="Blah blah blah fixes CVE-2020-26258 and a few other issues",
            ghissue_refs={"example": ""},
            changed_files={"foo/bar/otherthing.xml", "pom.xml"},
            cve_refs=["CVE-2020-26258"],
        ),
        Commit(repository="repo2", commit_id="2", cve_refs=["CVE-2020-26258"]),
        Commit(
            repository="repo3",
            commit_id="3",
            message="Another commit that fixes CVE-2020-26258",
            ghissue_refs={"example": ""},
        ),
        Commit(
            repository="repo4",
            commit_id="4",
            message="Endless loop causes DoS vulnerability",
            changed_files={"foo/bar/otherthing.xml", "pom.xml"},
        ),
        Commit(
            repository="repo5",
            commit_id="7532d2fb0d6081a12c2a48ec854a81a8b718be62",
            message="Insecure deserialization",
            changed_files={
                "core/src/main/java/org/apache/cxf/workqueue/AutomaticWorkQueueImpl.java"
            },
        ),
    ]


@pytest.fixture
def advisory_record():
    return AdvisoryRecord(
        vulnerability_id="CVE-2020-26258",
        repository_url="https://github.com/apache/struts",
        published_timestamp=1607532756,
        references=["https://reference.to/some/commit/7532d2fb0d60"],
        keywords=["AutomaticWorkQueueImpl"],
        paths=["pom.xml"],
    )


def test_apply_rules_all(candidates: List[Commit], advisory_record: AdvisoryRecord):
    annotated_candidates = apply_rules(candidates, advisory_record)

    assert len(annotated_candidates[0].matched_rules) == 4
    assert annotated_candidates[0].matched_rules[0][0] == "CVE_ID_IN_MESSAGE"
    assert "CVE-2020-26258" in annotated_candidates[0].matched_rules[0][1]

    # assert len(annotated_candidates[0].annotations) > 0
    # assert "REF_ADV_VULN_ID" in annotated_candidates[0].annotations
    # assert "REF_GH_ISSUE" in annotated_candidates[0].annotations
    # assert "CH_REL_PATH" in annotated_candidates[0].annotations

    # assert len(annotated_candidates[1].annotations) > 0
    # assert "REF_ADV_VULN_ID" in annotated_candidates[1].annotations
    # assert "REF_GH_ISSUE" not in annotated_candidates[1].annotations
    # assert "CH_REL_PATH" not in annotated_candidates[1].annotations

    # assert len(annotated_candidates[2].annotations) > 0
    # assert "REF_ADV_VULN_ID" not in annotated_candidates[2].annotations
    # assert "REF_GH_ISSUE" in annotated_candidates[2].annotations
    # assert "CH_REL_PATH" not in annotated_candidates[2].annotations

    # assert len(annotated_candidates[3].annotations) > 0
    # assert "REF_ADV_VULN_ID" not in annotated_candidates[3].annotations
    # assert "REF_GH_ISSUE" not in annotated_candidates[3].annotations
    # assert "CH_REL_PATH" in annotated_candidates[3].annotations
    # assert "SEC_KEYWORD_IN_COMMIT_MSG" in annotated_candidates[3].annotations

    # assert "SEC_KEYWORD_IN_COMMIT_MSG" in annotated_candidates[4].annotations
    # assert "TOKENS_IN_MODIFIED_PATHS" in annotated_candidates[4].annotations
    # assert "COMMIT_MENTIONED_IN_ADV" in annotated_candidates[4].annotations


def test_apply_rules_selected(
    candidates: List[Commit], advisory_record: AdvisoryRecord
):
    annotated_candidates = apply_rules(
        candidates=candidates,
        advisory_record=advisory_record,
        rules=[
            "REF_ADV_VULN_ID",
            "REF_GH_ISSUE",
            "CH_REL_PATH",
            "SEC_KEYWORD_IN_COMMIT_MSG",
            "TOKENS_IN_MODIFIED_PATHS",
            "COMMIT_MENTIONED_IN_ADV",
        ],
    )

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
    assert "COMMIT_MENTIONED_IN_ADV" in annotated_candidates[4].annotations


def test_apply_rules_selected_rules(
    candidates: List[Commit], advisory_record: AdvisoryRecord
):
    annotated_candidates = apply_rules(
        candidates=candidates,
        advisory_record=advisory_record,
        rules=["ALL", "-REF_ADV_VULN_ID"],
    )

    assert len(annotated_candidates[0].annotations) > 0
    assert "REF_ADV_VULN_ID" not in annotated_candidates[0].annotations
    assert "REF_GH_ISSUE" in annotated_candidates[0].annotations
    assert "CH_REL_PATH" in annotated_candidates[0].annotations


def test_sec_keywords_in_linked_issue():
    print("TODO")
