from pydantic import BaseModel

from datamodel.commit import Commit


class CommitFeatures(BaseModel):
    commit: Commit
    references_vuln_id: bool = False
    time_between_commit_and_advisory_record: int = 0
    changes_relevant_path: bool = False
    commit_falls_in_given_interval_based_on_advisory_publicatation_date: bool = False
