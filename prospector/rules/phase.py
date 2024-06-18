from abc import abstractmethod
from typing import List

from datamodel.commit import Commit
from rules.rule import Rule
from stats.execution import execution_statistics

rule_statistics = execution_statistics.sub_collection("rules")


class Phase:
    """An abstract class for a rule phase. All rules of a phase will be applied to the candidate commits.

    If you want to create a new phase, inherit from this class and implement the apply_rules() method.
    """

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def apply_rules(self, candidates: List[Commit], rules):
        pass

    @abstractmethod
    def get_enabled_rules(self, rules: List[str]) -> List[Rule]:
        pass

    def get_name(self):
        return self.name
