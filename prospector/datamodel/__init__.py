# from dataclasses import dataclass
from dataclasses import asdict


class BaseModel:
    def asDict(self):
        return asdict(self)
