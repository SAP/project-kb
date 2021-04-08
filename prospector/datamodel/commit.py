from dataclasses import dataclass, field

from . import BaseModel


@dataclass
class Commit(BaseModel):
    commit_id: str
    repository: str
    feature_1: str = ""
    log_msg: str = ""
    diff: "list[list[str]]" = field(default_factory=list)
    hunks: "list[list[str]]" = field(default_factory=list)
    hunk_count: int = 0
    jira_refs: "list[str]" = field(default_factory=list)
    ghissue_refs: "list[str]" = field(default_factory=list)
    cve_refs: "list[str]" = field(default_factory=list)
