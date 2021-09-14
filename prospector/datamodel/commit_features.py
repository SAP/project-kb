from typing import Any, Dict, List, TypeVar

from pydantic import BaseModel, Field

from datamodel.commit import Commit

PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")


# TODO drop this class; we can add a suitable "lrcache" annotation to feature extraction
# functions so we do not need to explicitly store the "extended" attributes of this class
# (the inner) Commit is all we need for rules (after we change the signatures of apply_rule_* functions)
class CommitWithFeatures(BaseModel):
    commit: Commit
    references_vuln_id: bool = False
    time_between_commit_and_advisory_record: int = 0
    changes_relevant_path: List[str] = ()
    other_CVE_in_message: List[str] = ()
    referred_to_by_pages_linked_from_advisories: List[str] = ()
    referred_to_by_nvd: List[str] = ()

    # TODO: move this field to datamodel.commit.Commit
    annotations: Dict[str, str] = Field(default_factory=dict)
    similarities_with_changed_files: PandasDataFrame

    def __init__(self, **data: Any):
        super().__init__(**data)

    def __hash__(self) -> int:
        # this function is needed to make the CommitWithFeatures object hashable
        # in particular, this is used in the filter_rank module
        return hash(self.commit.commit_id)
