from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field
from datasketch.lean_minhash import LeanMinHash
from util.lsh import build_lsh_index, compute_minhash, decode_minhash, encode_minhash

from datamodel.nlp import (
    extract_cve_references,
    extract_ghissue_references,
    extract_jira_references,
)
from git.raw_commit import RawCommit


class Commit(BaseModel):
    """
    Remember to propagate any changes you make here to the DB schema and
    to the save() and lookup() functions of the database module.
    """

    # TODO: a more elegant fix
    # Why are we using BaseModel
    class Config:
        arbitrary_types_allowed = True

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
    relevance: Optional[int] = 0
    matched_rules: List[Dict[str, Union[str, int]]] = Field(default_factory=list)
    minhash: LeanMinHash = None

    @property
    def hunk_count(self):
        return len(self.hunks)

    # These two methods allow to sort by relevance
    def __lt__(self, other: "Commit") -> bool:
        return self.relevance < other.relevance

    def __eq__(self, other: "Commit") -> bool:
        return self.relevance == other.relevance

    def add_match(self, rule: Dict[str, Any]):
        self.matched_rules.append(rule)

    def compute_relevance(self):
        self.relevance = sum([rule.get("relevance") for rule in self.matched_rules])

    def get_relevance(self) -> int:
        return sum([rule.get("relevance") for rule in self.matched_rules])

    def print(self):
        out = f"Commit: {self.commit_id}\nRepository: {self.repository}\nMessage: {self.message}\nTags: {self.tags}\n"
        print(out)

    def serialize_minhash(self):
        return encode_minhash(self.minhash)

    def deserialize_minhash(self, binary_minhash):
        self.minhash = decode_minhash(binary_minhash)

    def as_dict(self):
        return {
            "commit_id": self.commit_id,
            "repository": self.repository,
            "timestamp": self.timestamp,
            "hunks": self.hunks,
            "message": self.message,
            "diff": self.diff,
            "changed_files": self.changed_files,
            "message_reference_content": self.message_reference_content,
            "jira_refs": self.jira_refs,
            "ghissue_refs": self.ghissue_refs,
            "cve_refs": self.cve_refs,
            "tags": self.tags,
            "minhash": encode_minhash(self.minhash),
        }

    def find_twin(self, commit_list: List["Commit"]):
        index = build_lsh_index()
        for commit in commit_list:
            index.insert(commit.commit_id, commit.minhash)

        result = index.query(self.minhash)

        # Might be empty
        return [id for id in result if id != self.commit_id]


def make_from_dict(dict: Dict[str, Any]) -> Commit:
    """
    This function is responsible of translating a dict into a Commit object.
    """
    return Commit(
        commit_id=dict["commit_id"],
        repository=dict["repository"],
        timestamp=dict["timestamp"],
        hunks=dict["hunks"],
        message=dict["message"],
        diff=dict["diff"],
        changed_files=dict["changed_files"],
        message_reference_content=dict["message_reference_content"],
        jira_refs=dict["jira_refs"],
        ghissue_refs=dict["ghissue_refs"],
        cve_refs=dict["cve_refs"],
        tags=dict["tags"],
        minhash=decode_minhash(dict["minhash"]),
    )


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
        commit_id=raw_commit.get_id(), repository=raw_commit.get_repository_url()
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
    commit.minhash = compute_minhash(
        commit.message[:64]
    )  # TODO: Only if is the first time

    return commit
