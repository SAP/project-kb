from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from datamodel.nlp import (
    extract_cve_references,
    extract_ghissue_references,
    extract_jira_references,
)
from git.git import RawCommit


class Commit(BaseModel):
    """
    Remember to propagate any changes you make here to the DB schema and
    to the save() and lookup() functions of the database module.
    """

    commit_id: str = ""
    repository: str = ""
    timestamp: Optional[int] = 0
    hunks: List[Tuple[int, int]] = Field(default_factory=list)
    message: Optional[str] = ""
    diff: List[str] = Field(default_factory=list)
    changed_files: List[str] = Field(default_factory=list)
    message_reference_content: List[str] = Field(default_factory=list)
    jira_refs: Dict[str, str] = Field(default_factory=dict)
    ghissue_refs: Dict[str, str] = Field(default_factory=dict)
    cve_refs: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    annotations: Dict[str, str] = Field(default_factory=dict)
    relevance: Optional[int] = 0

    @property
    def hunk_count(self):
        return len(self.hunks)

    # These two methods allow to sort by relevance
    def __lt__(self, other) -> bool:
        return self.relevance < other.relevance

    def __eq__(self, other) -> bool:
        return self.relevance == other.relevance

    # def format(self):
    #     out = "Commit: {} {}".format(self.repository.get_url(), self.commit_id)
    #     out += "\nhunk_count: %d   diff_size: %d" % (self.hunk_count, len(self.diff))
    #     return out

    def print(self):
        out = f"Commit: {self.commit_id}\nRepository: {self.repository}\nMessage: {self.message}\nTags: {self.tags}\n"
        print(out)


def apply_ranking(candidates: List[Commit]) -> List[Commit]:
    """
    This function is responsible for ranking the list of commits
    according to their relevance to the advisory record.
    """
    return sorted(candidates, reverse=True)


def make_from_raw_commit(raw_commit: RawCommit) -> Commit:
    """
    This function is responsible of translating a RawCommit (git)
    into a preprocessed Commit, that can be saved to the DB
    and later used by the ranking/ML module.
    """
    commit = Commit(
        commit_id=raw_commit.get_id(), repository=raw_commit.get_repository()
    )

    # This is where all the attributes of the preprocessed commit
    # are computed and assigned.
    #
    # NOTE: all attributes that do not depend on a particular query
    # (e.g. do not depend on a particular Advisory Record)
    # should be computed here so that they can be stored in the db.
    # Space-efficiency is important.
    commit.diff = raw_commit.get_diff()

    commit.hunks = raw_commit.get_hunks()
    commit.message = raw_commit.get_msg()
    commit.timestamp = int(raw_commit.get_timestamp())

    commit.changed_files = raw_commit.get_changed_files()

    commit.tags = raw_commit.get_tags()
    commit.jira_refs = extract_jira_references(commit.message)
    commit.ghissue_refs = extract_ghissue_references(commit.repository, commit.message)
    commit.cve_refs = extract_cve_references(commit.message)

    return commit
