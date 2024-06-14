from abc import abstractmethod
from typing import Tuple

from langchain_core.language_models.llms import LLM

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit
from llm.llm_service import LLMService


class LLMRule:
    llm_service: LLMService

    def __init__(self, id: str, relevance: int):
        self.id = id
        self.message = ""
        self.relevance = relevance

    @abstractmethod
    def apply(
        self,
        candidate: Commit,
        advisory_record: AdvisoryRecord,
        llm_service: LLM,
    ) -> bool:
        pass

    def get_message(self):
        return self.message

    def as_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "relevance": self.relevance,
        }

    def get_rule_as_tuple(self) -> Tuple[str, str, int]:
        return (self.id, self.message, self.relevance)
