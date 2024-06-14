import re
from abc import abstractmethod
from typing import List, Tuple

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from datamodel.nlp import clean_string, find_similar_words
from rules.helpers import extract_security_keywords
from rules.nlp_rules import (
    AdvKeywordsInFiles,
    AdvKeywordsInMsg,
    ChangesRelevantCode,
    ChangesRelevantFiles,
    CommitHasTwins,
    CommitMentionedInReference,
    CrossReferencedBug,
    CrossReferencedGh,
    ReferencesBug,
    ReferencesGhIssue,
    RelevantWordsInMessage,
    SecurityKeywordInLinkedBug,
    SecurityKeywordInLinkedGhIssue,
    SecurityKeywordsInMsg,
    VulnIdInLinkedIssue,
    VulnIdInMessage,
)
from rules.rule import Rule
from stats.execution import Counter, execution_statistics
from util.lsh import build_lsh_index, decode_minhash

rule_statistics = execution_statistics.sub_collection("rules")


def apply_rules(
    candidates: List[Commit],
    advisory_record: AdvisoryRecord,
    rules=["ALL"],
) -> List[Commit]:
    enabled_rules = get_enabled_rules(rules)

    rule_statistics.collect("active", len(enabled_rules), unit="rules")

    Rule.lsh_index = build_lsh_index()

    for candidate in candidates:
        Rule.lsh_index.insert(candidate.commit_id, decode_minhash(candidate.minhash))

    with Counter(rule_statistics) as counter:
        counter.initialize("matches", unit="matches")
        for candidate in candidates:
            for rule in enabled_rules:
                if rule.apply(candidate, advisory_record):
                    counter.increment("matches")
                    candidate.add_match(rule.as_dict())
            candidate.compute_relevance()

    # for candidate in candidates:
    #     if candidate.has_twin():
    #         for twin in candidate.twins:
    #             for other_candidate in candidates:
    #                 if (
    #                     other_candidate.commit_id == twin[1]
    #                     and other_candidate.relevance > candidate.relevance
    #                 ):
    #                     candidate.relevance = other_candidate.relevance
    #                     # Add a reason on why we are doing this.

    return candidates


def get_enabled_rules(rules: List[str]) -> List[Rule]:
    if "ALL" in rules:
        return RULES

    enabled_rules = []
    for r in RULES:
        if r.id in rules:
            enabled_rules.append(r)

    return enabled_rules


RULES: List[Rule] = [
    VulnIdInMessage("VULN_ID_IN_MESSAGE", 64),
    # CommitMentionedInAdv("COMMIT_IN_ADVISORY", 64),
    CrossReferencedBug("XREF_BUG", 32),
    CrossReferencedGh("XREF_GH", 32),
    CommitMentionedInReference("COMMIT_IN_REFERENCE", 64),
    VulnIdInLinkedIssue("VULN_ID_IN_LINKED_ISSUE", 32),
    ChangesRelevantFiles("CHANGES_RELEVANT_FILES", 8),
    ChangesRelevantCode("CHANGES_RELEVANT_CODE", 8),
    RelevantWordsInMessage("RELEVANT_WORDS_IN_MESSAGE", 8),
    AdvKeywordsInFiles("ADV_KEYWORDS_IN_FILES", 4),
    AdvKeywordsInMsg("ADV_KEYWORDS_IN_MSG", 4),
    SecurityKeywordsInMsg("SEC_KEYWORDS_IN_MESSAGE", 4),
    SecurityKeywordInLinkedGhIssue("SEC_KEYWORDS_IN_LINKED_GH", 4),
    SecurityKeywordInLinkedBug("SEC_KEYWORDS_IN_LINKED_BUG", 4),
    ReferencesGhIssue("GITHUB_ISSUE_IN_MESSAGE", 2),
    ReferencesBug("BUG_IN_MESSAGE", 2),
    CommitHasTwins("COMMIT_HAS_TWINS", 2),
]

rules_list = [
    "COMMIT_IN_REFERENCE",
    "VULN_ID_IN_MESSAGE",
    "VULN_ID_IN_LINKED_ISSUE",
    "XREF_BUG",
    "XREF_GH",
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

# print(" & ".join([f"\\rot{{{x}}}" for x in rules_list]))
