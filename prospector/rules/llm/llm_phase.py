from typing import List

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit, apply_ranking
from llm.llm_service import LLMService
from llm.model_instantiation import create_model_instance
from rules.llm.llm_rules import CommitIsSecurityRelevant, LLMRule
from rules.phase import Phase, rule_statistics
from stats.execution import Counter
from util.config_parser import LLMServiceConfig

LLM_RULES: List[LLMRule] = [CommitIsSecurityRelevant("COMMIT_IS_SECURITY_RELEVANT", 32)]


class LLMPhase(Phase):
    """Implementes the NLP phase in which all NLP rules are applied."""

    def __init__(self, llm_service_config: LLMServiceConfig):
        super().__init__("LLM Phase")
        self.rules = LLM_RULES
        self._llm_service_config = llm_service_config
        self._llm_service = create_model_instance(llm_service_config)

    def apply_rules(self, candidates: List[Commit], rules=["ALL"]) -> List[Commit]:
        enabled_rules = self.get_enabled_rules(rules)

        rule_statistics.collect("active", len(enabled_rules), unit="rules")

        with Counter(rule_statistics) as counter:
            counter.initialize("matches", unit="matches")
            for candidate in candidates:
                for rule in enabled_rules:
                    if rule.apply(
                        candidate, self._llm_service, self._llm_service_config
                    ):
                        counter.increment("matches")
                        candidate.add_match(rule.as_dict())
                candidate.compute_relevance()

        return apply_ranking(candidates)

    def get_enabled_rules(self, rules: List[str]) -> List[LLMRule]:
        if "ALL" in rules:
            return LLM_RULES

        enabled_rules = []
        for r in LLM_RULES:
            if r.id in rules:
                enabled_rules.append(r)

        return enabled_rules

    def get_name(self):
        return super().get_name()
