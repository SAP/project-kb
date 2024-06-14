from abc import abstractmethod
from typing import Tuple

from datamodel.advisory import AdvisoryRecord
from datamodel.commit import Commit


class Rule:
    def __init__(self, id: str, relevance: int):
        self.id = id
        self.message = ""
        self.relevance = relevance

    @abstractmethod
    def apply(self, candidate: Commit, advisory_record: AdvisoryRecord) -> bool:
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
