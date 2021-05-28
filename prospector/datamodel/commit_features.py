from typing import Any

from pydantic import BaseModel

from datamodel.commit import Commit


class CommitWithFeatures(BaseModel):
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

    def __init__(self, **data: Any):
        super().__init__(**data)

        self.n_hunks = self.commit.hunk_count

        if self.n_hunks > 0:
            hunk_lengths = [hunk[1] - hunk[0] for hunk in self.commit.hunks]
            self.avg_hunk_size = sum(hunk_lengths) / self.n_hunks
        else:
            self.avg_hunk_size = 0

        self.n_changed_files = len(self.commit.changed_files)

        self.references_ghissue = len(self.commit.ghissue_refs) > 0

        self.contains_jira_reference = len(self.commit.jira_refs) > 0

    def __hash__(self) -> int:
        # this function is needed to make the CommitWithFeatures object hashable
        # in particular, this is used in the filter_rank module
        return hash(self.commit.commit_id)
