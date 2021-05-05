from pydantic import BaseModel

from datamodel.commit import Commit


class CommitFeatures(BaseModel):
    commit: Commit
    references_vuln_id: bool = False
    references_ghissue: bool = False
    time_between_commit_and_advisory_record: int = 0
    changes_relevant_path: bool = False
    other_CVE_in_message: bool = False
    commit_falls_in_given_interval_based_on_advisory_publicatation_date: bool = False
    avg_hunk_size: int = 0
    n_hunks: int = 0
    n_changed_files: int = 0
    contains_jira_reference: bool = False
