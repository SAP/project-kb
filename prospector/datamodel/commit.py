import json
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field


class Commit(BaseModel):
    # class Commit:
    commit_id: Optional[str] = ""
    repository: str
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


def create_commit_object(commit_list):
    # Converts raw data of lookup() to a Commit object
    for i in (3, 6, 7, 8, 9, 10, 11, 12):
        if commit_list[i] == "{}":
            commit_list[i] = []
        else:
            commit_list[i] = json.dumps(commit_list[i])

    commit_obj = Commit(
        commit_id=commit_list[0],
        repository=commit_list[1],
        timestamp=commit_list[2],
        hunks=commit_list[3],
        hunk_count=commit_list[4],
        message=commit_list[5],
        diff=commit_list[6],
        changed_files=commit_list[7],
        message_reference_content=commit_list[8],
        jira_refs=commit_list[9],
        ghissue_refs=commit_list[10],
        cve_refs=commit_list[11],
        tags=commit_list[12],
    )
    return commit_obj


# def format(self):
#     out = "Commit: {} {}".format(self.repository.get_url(), self.commit_id)
#     out += "\nhunk_count: %d   diff_size: %d" % (self.hunk_count, len(self.diff))
#     return out
