from typing import List, Optional, Tuple

from pydantic import BaseModel, Field


class Commit(BaseModel):
    # class Commit:
    commit_id: str = ""
    repository: str = ""
    timestamp: Optional[int] = 0
    hunks: List[Tuple[int, int]] = Field(default_factory=list)
    hunk_count: Optional[int] = 0
    message: Optional[str] = ""
    diff: List[str] = Field(default_factory=list)
    changed_files: List[str] = Field(default_factory=list)
    message_reference_content: List[str] = Field(default_factory=list)
    jira_refs: List[str] = Field(default_factory=list)
    ghissue_refs: List[str] = Field(default_factory=list)
    cve_refs: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # def format(self):
    #     out = "Commit: {} {}".format(self.repository.get_url(), self.commit_id)
    #     out += "\nhunk_count: %d   diff_size: %d" % (self.hunk_count, len(self.diff))
    #     return out
