from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from datamodel.nlp import (
    extract_cve_references,
    extract_ghissue_references,
    extract_jira_references,
)
from git.raw_commit import RawCommit
from util.lsh import decode_minhash, encode_minhash, get_encoded_minhash


class Commit(BaseModel):
    """
    Remember to propagate any changes you make here to the DB schema and
    to the save() and lookup() functions of the database module.
    """

    commit_id: str = ""
    repository: str = ""
    timestamp: Optional[int] = 0
    message: Optional[str] = ""
    hunks: Optional[int] = (
        0  # List[Tuple[int, int]] = Field(default_factory=list)
    )
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
    twins: List[List[str]] = Field(default_factory=list)
    security_relevant: Optional[bool] = None

    def to_dict(self):
        d = dict(self.__dict__)
        del d["matched_rules"]
        del d["relevance"]
        del d["twins"]
        return d

    def get_hunks(self):
        return self.hunks

    # These two methods allow to sort by relevance
    def __lt__(self, other: "Commit") -> bool:
        return self.relevance < other.relevance

    def __eq__(self, other: "Commit") -> bool:
        return self.relevance == other.relevance

    def add_match(self, rule: Dict[str, Any]):
        """Adds a rule to the commit's matched rules. Makes sure that the rule is added in order of relevance."""
        for i, r in enumerate(self.matched_rules):
            if rule["relevance"] == r["relevance"]:
                self.matched_rules.insert(i, rule)
                return

        self.matched_rules.append(rule)

    def has_twin(self):
        return len(self.twins) > 0

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def get_tag(self):
        return self.tags[0] if len(self.tags) else "no-tag"

    def compute_relevance(self):
        self.relevance = sum(
            [rule.get("relevance") for rule in self.matched_rules]
        )

    def get_relevance(self) -> int:
        return sum([rule.get("relevance") for rule in self.matched_rules])

    def print(self):
        out = f"Commit: {self.commit_id}\nRepository: {self.repository}\nMessage: {self.message}\nTags: {self.tags}\n"
        print(out)

    def serialize_minhash(self):
        return encode_minhash(self.minhash)

    def deserialize_minhash(self, binary_minhash):
        self.minhash = decode_minhash(binary_minhash)

    def as_dict(
        self, no_hash: bool = True, no_rules: bool = True, no_diff: bool = True
    ):
        out = {
            "commit_id": self.commit_id,
            "repository": self.repository,
            "timestamp": self.timestamp,
            "hunks": self.hunks,
            "message": self.message,
            "changed_files": self.changed_files,
            "message_reference_content": self.message_reference_content,
            "jira_refs": self.jira_refs,
            "ghissue_refs": self.ghissue_refs,
            "cve_refs": self.cve_refs,
            "twins": self.twins,
            "tags": self.tags,
        }
        if not no_diff:
            out["diff"] = self.diff
        if not no_hash:
            out["minhash"] = encode_minhash(self.minhash)
        if not no_rules:
            out["matched_rules"] = self.matched_rules
        return out


def apply_ranking(candidates: List[Commit]) -> List[Commit]:
    """
    This function is responsible for ranking the list of commits
    according to their relevance to the advisory record.
    """
    return sorted(candidates, reverse=True)


def make_from_raw_commit(raw: RawCommit, get_tags: bool = False) -> Commit:
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
    )

    # NOTE: all attributes that do not depend on a particular query
    # (e.g. do not depend on a particular Advisory Record)
    # should be computed here so that they can be stored in the db.
    # Space-efficiency is important.
    commit.minhash = get_encoded_minhash(raw.get_msg(50))

    if not get_tags:
        # commit.tags = [commit.tags[0]] if len(commit.tags) else ["no-tag"]
        commit.tags = ["no-tag"]
        # return commit
    else:
        commit.tags = raw.find_tags()

    commit.diff, commit.hunks = raw.get_diff()
    commit.jira_refs = extract_jira_references(
        commit.repository, commit.message
    )
    commit.ghissue_refs = extract_ghissue_references(
        commit.repository, commit.message
    )
    commit.cve_refs = extract_cve_references(commit.message)
    return commit
