from dataclasses import dataclass
from . import BaseModel


@dataclass
class User(BaseModel):
    id: str
    firstname: str
    lastname: str = ""
    hashed_password: str = ""
