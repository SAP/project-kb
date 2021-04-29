from pydantic import BaseModel

from datamodel.commit import Commit


class CommitFeatures(BaseModel):
    commit: Commit
    references_vuln_id: bool = False
    references_ghissue: bool = False
    time_between_commit_and_advisory_record: int = 0
    changes_relevant_path: bool = False
    n_hunks: int = 0
    n_changed_files: int = 0
    contains_jira_reference: bool = False
