from typing import List

import pytest
from requests_cache import Optional

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from rules.rules import RULES_PHASE_1, apply_rules
from util.lsh import get_encoded_minhash

# from datamodel.commit_features import CommitWithFeatures

MOCK_CVE_ID = "CVE-2020-26258"

enabled_rules_from_config = [
    "VULN_ID_IN_MESSAGE",
    "XREF_BUG",
    "XREF_GH",
    "COMMIT_IN_REFERENCE",
    "VULN_ID_IN_LINKED_ISSUE",
    "CHANGES_RELEVANT_FILES",
    "CHANGES_RELEVANT_CODE",
    "RELEVANT_WORDS_IN_MESSAGE",
    "ADV_KEYWORDS_IN_FILES",
    "ADV_KEYWORDS_IN_MSG",
    "SEC_KEYWORDS_IN_MESSAGE",
    "SEC_KEYWORDS_IN_LINKED_GH",
    "SEC_KEYWORDS_IN_LINKED_BUG",
    "GITHUB_ISSUE_IN_MESSAGE",
    "BUG_IN_MESSAGE",
    "COMMIT_HAS_TWINS",
]


def get_msg(text, limit_length: Optional[int] = None) -> str:
    return text[:limit_length] if limit_length else text


@pytest.fixture
def candidates():
    return [
        # Should match: VulnIdInMessage, ReferencesGhIssue
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
            minhash=get_encoded_minhash(get_msg("")),
        ),
        # Should match: VulnIdInMessage, ReferencesGhIssue
        Commit(
            repository="repo3",
            commit_id="3234567890",
            message=f"Another commit that fixes {MOCK_CVE_ID}",
            ghissue_refs={"example": ""},
            cve_refs=[f"{MOCK_CVE_ID}"],
            minhash=get_encoded_minhash(
                get_msg(f"Another commit that fixes {MOCK_CVE_ID}", 50)
            ),
        ),
        # Should match: SecurityKeywordsInMsg
        Commit(
            repository="repo4",
            commit_id="4234567890",
            message="Endless loop causes DoS vulnerability",
            changed_files={"foo/bar/otherthing.xml", "pom.xml"},
            minhash=get_encoded_minhash(
                get_msg("Endless loop causes DoS vulnerability", 50)
            ),
        ),
        # Should match: AdvKeywordsInFiles, SecurityKeywordsInMsg, CommitMentionedInReference
        Commit(
            repository="repo5",
            commit_id="7532d2fb0d6081a12c2a48ec854a81a8b718be62",
            message="Insecure deserialization",
            changed_files={
                "core/src/main/java/org/apache/cxf/workqueue/AutomaticWorkQueueImpl.java"
            },
            minhash=get_encoded_minhash(get_msg("Insecure deserialization", 50)),
        ),
        # TODO: Not matched by existing tests: GHSecurityAdvInMessage, ReferencesBug, ChangesRelevantCode, TwinMentionedInAdv, VulnIdInLinkedIssue, SecurityKeywordInLinkedGhIssue, SecurityKeywordInLinkedBug, CrossReferencedBug, CrossReferencedGh, CommitHasTwins, ChangesRelevantFiles, CommitMentionedInAdv, RelevantWordsInMessage
    ]


@pytest.fixture
def advisory_record():
    return AdvisoryRecord(
        cve_id=f"{MOCK_CVE_ID}",
        repository_url="https://github.com/apache/struts",
        published_timestamp=1607532756,
        references={
            "https://reference.to/some/commit/7532d2fb0d60": 1,
        },
        keywords=["AutomaticWorkQueueImpl"],
        # paths=["pom.xml"],
    )


def test_apply_phase_1_rules(candidates: List[Commit], advisory_record: AdvisoryRecord):
    annotated_candidates = apply_rules(
        candidates, advisory_record, enabled_rules=enabled_rules_from_config
    )

    # Repo 5: Should match: AdvKeywordsInFiles, SecurityKeywordsInMsg, CommitMentionedInReference
    assert len(annotated_candidates[0].matched_rules) == 3

    matched_rules_names = [item["id"] for item in annotated_candidates[0].matched_rules]
    assert "ADV_KEYWORDS_IN_FILES" in matched_rules_names
    assert "COMMIT_IN_REFERENCE" in matched_rules_names
    assert "SEC_KEYWORDS_IN_MESSAGE" in matched_rules_names

    # Repo 1: Should match: VulnIdInMessage, ReferencesGhIssue
    assert len(annotated_candidates[1].matched_rules) == 2

    matched_rules_names = [item["id"] for item in annotated_candidates[1].matched_rules]
    assert "VULN_ID_IN_MESSAGE" in matched_rules_names
    assert "GITHUB_ISSUE_IN_MESSAGE" in matched_rules_names

    # Repo 3: Should match: VulnIdInMessage, ReferencesGhIssue
    assert len(annotated_candidates[2].matched_rules) == 2

    matched_rules_names = [item["id"] for item in annotated_candidates[2].matched_rules]
    assert "VULN_ID_IN_MESSAGE" in matched_rules_names
    assert "GITHUB_ISSUE_IN_MESSAGE" in matched_rules_names

    # Repo 4: Should match: SecurityKeywordsInMsg
    assert len(annotated_candidates[3].matched_rules) == 1

    matched_rules_names = [item["id"] for item in annotated_candidates[3].matched_rules]
    assert "SEC_KEYWORDS_IN_MESSAGE" in matched_rules_names

    # Repo 2: Matches nothing
    assert len(annotated_candidates[4].matched_rules) == 0
