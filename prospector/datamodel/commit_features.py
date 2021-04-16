from dataclasses import dataclass, field

from datamodel.commit import Commit

from . import BaseModel


@dataclass
class CommitFeatures(BaseModel):
    commit: Commit
    reference_to_vuln_id: bool = False
