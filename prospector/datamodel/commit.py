from dataclasses import dataclass, field

from git.git import Git

from . import BaseModel

# from dataclasses_json import dataclass_json


# @dataclass_json
@dataclass
class Commit(BaseModel):
    commit_id: str
    repository: Git
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
        out = "Commit: {} {}".format(self.repository.get_url(), self.commit_id)
        out += "\nhunk_count: %d   diff_size: %d" % (self.hunk_count, len(self.diff))
        return out
