import json
from abc import abstractmethod
from typing import Tuple

import requests
from langchain_core.language_models.llms import LLM

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from llm.llm_service import LLMService
from rules.rule import Rule
from util.config_parser import LLMServiceConfig


class LLMRule(Rule):
    def __init__(self, id: str, relevance: int):
        super().__init__(id, relevance)

    @abstractmethod
    def apply(
        self,
        candidate: Commit,
        llm_service: LLMService,
        llm_service_config: LLMServiceConfig,
    ) -> bool:
        pass

    def get_message(self):
        return super().get_message()

    def as_dict(self):
        return super().as_dict()

    def get_rule_as_tuple(self) -> Tuple[str, str, int]:
        return super().get_rule_as_tuple()


class CommitIsSecurityRelevant(LLMRule):
    """Matches commits that are deemed security relevant by the commit classification service."""

    def apply(
        self,
        candidate: Commit,
        llm_service: LLMService,
        llm_service_config: LLMServiceConfig,
    ) -> bool:
        data = {
            "temperature": llm_service_config.temperature,
            "diff": "\n".join(candidate.diff),
        }

        response = requests.get("http://127.0.0.1:8001/predict", json=data)

        prediction = response.json()["prediction"]
        if prediction == "1":
            return True
        else:
            return False
