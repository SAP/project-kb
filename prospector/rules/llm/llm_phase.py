from typing import Counter, List

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit, apply_ranking
from rules.llm.llm_rules import LLMRule
from rules.phase import Phase, rule_statistics

LLM_RULES: List[LLMRule] = []


class LLMPhase(Phase):
    """Implementes the NLP phase in which all NLP rules are applied."""

    def __init__(self):
        super().__init__("LLM Phase")
        self.rules = LLM_RULES

    def apply_rules(
        self, candidates: List[Commit], advisory_record: AdvisoryRecord, rules=["ALL"]
    ) -> List[Commit]:
        enabled_rules = (
            self.rules
        )  # LASCHA: add here a similar implementation to get_enabled_rules()

        rule_statistics.collect("active", len(enabled_rules), unit="rules")

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
