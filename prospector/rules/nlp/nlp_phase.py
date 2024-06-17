from typing import List

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit, apply_ranking
from rules.nlp.nlp_rules import (
    AdvKeywordsInFiles,
    AdvKeywordsInMsg,
    ChangesRelevantCode,
    ChangesRelevantFiles,
    CommitHasTwins,
    CommitMentionedInReference,
    CrossReferencedBug,
    CrossReferencedGh,
    NLPRule,
    ReferencesBug,
    ReferencesGhIssue,
    RelevantWordsInMessage,
    SecurityKeywordInLinkedBug,
    SecurityKeywordInLinkedGhIssue,
    SecurityKeywordsInMsg,
    VulnIdInLinkedIssue,
    VulnIdInMessage,
)
from rules.phase import Phase, rule_statistics
from stats.execution import Counter
from util.lsh import build_lsh_index, decode_minhash

NLP_RULES: List[NLPRule] = [
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


class NLPPhase(Phase):
    """Implementes the NLP phase in which all NLP rules are applied."""

    def __init__(self):
        super().__init__("NLP Phase")
        self.rules = NLP_RULES

    def apply_rules(
        self, candidates: List[Commit], advisory_record: AdvisoryRecord, rules=["ALL"]
    ) -> List[Commit]:
        # apply the NLP rules
        enabled_rules = (
            self.rules
        )  # LASCHA: add here a similar implementation to get_enabled_rules()

        rule_statistics.collect("active", len(enabled_rules), unit="rules")

        NLPRule.lsh_index = build_lsh_index()

        for candidate in candidates:
            NLPRule.lsh_index.insert(
                candidate.commit_id, decode_minhash(candidate.minhash)
            )

        with Counter(rule_statistics) as counter:
            counter.initialize("matches", unit="matches")
            for candidate in candidates:
                for rule in enabled_rules:
                    if rule.apply(candidate, advisory_record):
                        counter.increment("matches")
                        candidate.add_match(rule.as_dict())
                candidate.compute_relevance()

        return apply_ranking(candidates)

    def get_name(self):
        return super().get_name()
