# from dataclasses import dataclass
from dataclasses import asdict


class BaseModel:
    def as_dict(self):
        return asdict(self)
