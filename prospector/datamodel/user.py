"""
This module contains code related to users
"""
from dataclasses import dataclass

from . import BaseModel


@dataclass
class User(BaseModel):
    """
    This represents a user of the REST API
    """

    user_id: str
    firstname: str
    lastname: str = ""
    hashed_password: str = ""
