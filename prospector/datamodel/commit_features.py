from typing import Any, Dict, List, TypeVar

from pydantic import BaseModel, Field

from datamodel.commit import Commit

PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")


class CommitWithFeatures(BaseModel):
    commit: Commit
    references_vuln_id: bool = False
    time_between_commit_and_advisory_record: int = 0
    changes_relevant_path: List[str] = ()
    other_CVE_in_message: List[str] = ()
    referred_to_by_pages_linked_from_advisories: List[str] = ()
    referred_to_by_nvd: List[str] = ()
    annotations: Dict[str, str] = Field(default_factory=dict)
    similarities_with_changed_files: PandasDataFrame

    def __init__(self, **data: Any):
        super().__init__(**data)

    def __hash__(self) -> int:
        # this function is needed to make the CommitWithFeatures object hashable
        # in particular, this is used in the filter_rank module
        return hash(self.commit.commit_id)
