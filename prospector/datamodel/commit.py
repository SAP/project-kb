from dataclasses import dataclass
from . import BaseModel


@dataclass
class Commit(BaseModel):
    id: str
    repository: str
    feature_1: str = ""
    feature_2: str = ""
