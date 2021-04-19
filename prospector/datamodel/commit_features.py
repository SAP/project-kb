from pydantic import BaseModel

from datamodel.commit import Commit


class CommitFeatures(BaseModel):
    commit: Commit
    references_vuln_id: bool = False
