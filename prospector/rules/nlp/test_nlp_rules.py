from typing import List

import pytest
from requests_cache import Optional

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from rules.nlp.nlp_phase import NLPPhase
from util.lsh import get_encoded_minhash

# from datamodel.commit_features import CommitWithFeatures

MOCK_CVE_ID = "CVE-2020-26258"


def get_msg(text, limit_length: Optional[int] = None) -> str:
    return text[:limit_length] if limit_length else text


@pytest.fixture
def candidates():
    return [
        Commit(
            repository="repo1",
            commit_id="1234567890",
            message=f"Blah blah blah fixes {MOCK_CVE_ID} and a few other issues",
            ghissue_refs={"example": ""},
            changed_files={"foo/bar/otherthing.xml", "pom.xml"},
            cve_refs=[f"{MOCK_CVE_ID}"],
            minhash=get_encoded_minhash(
                get_msg(
                    f"Blah blah blah fixes {MOCK_CVE_ID} and a few other issues",
                    50,
                )
            ),
        ),
        Commit(
            repository="repo2",
            commit_id="2234567890",
            message="",
            cve_refs=[f"{MOCK_CVE_ID}"],
            minhash=get_encoded_minhash(get_msg("")),
        ),
        Commit(
            repository="repo3",
            commit_id="3234567890",
            message=f"Another commit that fixes {MOCK_CVE_ID}",
            ghissue_refs={"example": ""},
            minhash=get_encoded_minhash(
                get_msg(f"Another commit that fixes {MOCK_CVE_ID}", 50)
            ),
        ),
        Commit(
            repository="repo4",
            commit_id="4234567890",
            message="Endless loop causes DoS vulnerability",
            changed_files={"foo/bar/otherthing.xml", "pom.xml"},
            minhash=get_encoded_minhash(
                get_msg("Endless loop causes DoS vulnerability", 50)
            ),
        ),
        Commit(
            repository="repo5",
            commit_id="7532d2fb0d6081a12c2a48ec854a81a8b718be62",
            message="Insecure deserialization",
            changed_files={
                "core/src/main/java/org/apache/cxf/workqueue/AutomaticWorkQueueImpl.java"
            },
            minhash=get_encoded_minhash(get_msg("Insecure deserialization", 50)),
        ),
    ]


@pytest.fixture
def advisory_record():
    return AdvisoryRecord(
        cve_id=f"{MOCK_CVE_ID}",
        repository_url="https://github.com/apache/struts",
        published_timestamp=1607532756,
        references={"https://reference.to/some/commit/7532d2fb0d60": 1},
        keywords=["AutomaticWorkQueueImpl"],
        # paths=["pom.xml"],
    )


def test_apply_rules_all(candidates: List[Commit], advisory_record: AdvisoryRecord):
    annotated_candidates = NLPPhase().apply_rules(
        candidates, advisory_record, rules=["ALL"]
    )

    assert len(annotated_candidates[0].matched_rules) == 3
    assert annotated_candidates[0].matched_rules[0].get("id") == "COMMIT_IN_REFERENCE"

    matched_rules_names = [item["id"] for item in annotated_candidates[0].matched_rules]
    assert "ADV_KEYWORDS_IN_FILES" in matched_rules_names
    assert "COMMIT_IN_REFERENCE" in matched_rules_names
    assert "SEC_KEYWORDS_IN_MESSAGE" in matched_rules_names

    matched_rules_names = [item["id"] for item in annotated_candidates[1].matched_rules]
    assert len(matched_rules_names) > 0
    assert "VULN_ID_IN_MESSAGE" in matched_rules_names
    assert "GITHUB_ISSUE_IN_MESSAGE" not in matched_rules_names

    matched_rules_names = [item["id"] for item in annotated_candidates[2].matched_rules]
    assert len(matched_rules_names) > 0
    assert "VULN_ID_IN_MESSAGE" not in matched_rules_names

    matched_rules_names = [item["id"] for item in annotated_candidates[3].matched_rules]
    assert len(matched_rules_names) > 0
    assert "SEC_KEYWORDS_IN_MESSAGE" not in matched_rules_names

    matched_rules_names = [item["id"] for item in annotated_candidates[4].matched_rules]

    assert "GITHUB_ISSUE_IN_MESSAGE" in matched_rules_names


def test_apply_rules_selected(
    candidates: List[Commit], advisory_record: AdvisoryRecord
):
    annotated_candidates = NLPPhase().apply_rules(
        candidates=candidates,
        advisory_record=advisory_record,
        rules=[
            "SEC_KEYWORDS_IN_MESSAGE",
            "ADV_KEYWORDS_IN_FILES",
            "COMMIT_IN_REFERENCE",
            "VULN_ID_IN_MESSAGE",
        ],
    )

    print(annotated_candidates[0].to_dict())
    print(
        annotated_candidates[0].matched_rules,
    )

    matched_rules_names = [item["id"] for item in annotated_candidates[0].matched_rules]
    assert len(matched_rules_names) > 0
    assert "ADV_KEYWORDS_IN_FILES" in matched_rules_names
    assert "COMMIT_IN_REFERENCE" in matched_rules_names
    assert "SEC_KEYWORDS_IN_MESSAGE" in matched_rules_names

    matched_rules_names = [item["id"] for item in annotated_candidates[1].matched_rules]
    assert len(matched_rules_names) > 0
    assert "VULN_ID_IN_MESSAGE" in matched_rules_names
    assert "GITHUB_ISSUE_IN_MESSAGE" not in matched_rules_names

    matched_rules_names = [item["id"] for item in annotated_candidates[2].matched_rules]
    assert len(matched_rules_names) > 0
    assert "VULN_ID_IN_MESSAGE" in matched_rules_names

    matched_rules_names = [item["id"] for item in annotated_candidates[3].matched_rules]
    assert len(matched_rules_names) > 0
    assert "SEC_KEYWORDS_IN_MESSAGE" in matched_rules_names

    matched_rules_names = [item["id"] for item in annotated_candidates[4].matched_rules]

    assert len(matched_rules_names) == 0
