from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from datamodel.nlp import (
    extract_cve_references,
    extract_ghissue_references,
    extract_jira_references,
)
from git.raw_commit import RawCommit
from util.lsh import build_lsh_index, decode_minhash, encode_minhash


class Commit(BaseModel):
    """
    Remember to propagate any changes you make here to the DB schema and
    to the save() and lookup() functions of the database module.
    """

    commit_id: str = ""
    repository: str = ""
    timestamp: Optional[int] = 0
    message: Optional[str] = ""
    hunks: Optional[int] = 0  # List[Tuple[int, int]] = Field(default_factory=list)
    diff: List[str] = Field(default_factory=list)
    changed_files: List[str] = Field(default_factory=list)
    message_reference_content: List[str] = Field(default_factory=list)
    jira_refs: Dict[str, str] = Field(default_factory=dict)
    ghissue_refs: Dict[str, str] = Field(default_factory=dict)
    cve_refs: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    relevance: Optional[int] = 0
    matched_rules: List[Dict[str, str | int]] = Field(default_factory=list)
    minhash: Optional[str] = ""
    twins: List[str] = Field(default_factory=list)

    def to_dict(self):
        d = dict(self.__dict__)
        del d["matched_rules"]
        del d["relevance"]
        return d

    def get_hunks(self):
        return self.hunks

    # These two methods allow to sort by relevance
    def __lt__(self, other: "Commit") -> bool:
        return self.relevance < other.relevance

    def __eq__(self, other: "Commit") -> bool:
        return self.relevance == other.relevance

    def add_match(self, rule: Dict[str, Any]):
        for i, r in enumerate(self.matched_rules):
            if rule["relevance"] == r["relevance"]:
                self.matched_rules.insert(i, rule)
                return

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

    def as_dict(self, no_hash: bool = True, no_rules: bool = True):
        out = {
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
        }
        if not no_hash:
            out["minhash"] = encode_minhash(self.minhash)
        if not no_rules:
            out["matched_rules"] = self.matched_rules
        return out

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
        # decode_minhash(dict["minhash"]),
    )


def apply_ranking(candidates: List[Commit]) -> List[Commit]:
    """
    This function is responsible for ranking the list of commits
    according to their relevance to the advisory record.
    """
    return sorted(candidates, reverse=True)


def make_from_raw_commit(raw: RawCommit) -> Commit:
    """
    This function is responsible of translating a RawCommit (git)
    into a preprocessed Commit, that can be saved to the DB
    and later used by the ranking/ML module.
    """

    commit = Commit(
        commit_id=raw.get_id(),
        repository=raw.get_repository_url(),
        timestamp=raw.get_timestamp(),
        changed_files=raw.get_changed_files(),
        message=raw.get_msg(),
        twins=raw.get_twins(),
        minhash=raw.get_minhash(),
    )

    # This is where all the attributes of the preprocessed commit
    # are computed and assigned.
    #
    # NOTE: all attributes that do not depend on a particular query
    # (e.g. do not depend on a particular Advisory Record)
    # should be computed here so that they can be stored in the db.
    # Space-efficiency is important.

    commit.diff, commit.hunks = raw.get_diff()
    if commit.hunks < 200:
        commit.tags = raw.get_tags()
        commit.jira_refs = extract_jira_references(commit.repository, commit.message)
        commit.ghissue_refs = extract_ghissue_references(
            commit.repository, commit.message
        )
        commit.cve_refs = extract_cve_references(commit.message)
    return commit
