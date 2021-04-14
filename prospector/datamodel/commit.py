from dataclasses import dataclass, field

from . import BaseModel


@dataclass
class Commit(BaseModel):
    commit_id: str
    repository: str
    feature_1: str = ""
    timestamp: int = 0
    hunks: "list[list[str]]" = field(default_factory=list)
    hunk_count: int = 0
    message: str = ""
    diff: "list[list[str]]" = field(default_factory=list)
    changed_files: "list[str]" = field(default_factory=list)
    message_reference_content: "list[str]" = field(default_factory=list)
    jira_refs: "list[str]" = field(default_factory=list)
    ghissue_refs: "list[str]" = field(default_factory=list)
    cve_refs: "list[str]" = field(default_factory=list)

    def format(self):
        out = "Commit: {} {}".format(self.repository, self.commit_id)
        out += "\nhunk_count: %d   diff_size: %d" % (self.hunk_count, len(self.diff))
        return out
