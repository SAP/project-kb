import os

# from pprint import pprint
from typing import List

from fastapi import APIRouter

from commitdb.postgres import PostgresCommitDB
from datamodel.commit import Commit

# from pydantic import BaseModel, Field


DB_CONNECT_STRING = "HOST={};DB={};UID={};PWD={};PORT={};".format(
    os.environ["POSTGRES_HOST"],
    os.environ["POSTGRES_DBNAME"],
    os.environ["POSTGRES_USER"],
    os.environ["POSTGRES_PASSWORD"],
    os.environ["POSTGRES_PORT"],
)


router = APIRouter(
    prefix="/commits",
    tags=["preprocessed_commits"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", tags=["preprocessed_commits"])
async def upload_preprocessed_commit(payload: List[Commit]):

    db = PostgresCommitDB()
    db.connect(DB_CONNECT_STRING)

    for commit in payload:
        db.save(commit)

    return payload
