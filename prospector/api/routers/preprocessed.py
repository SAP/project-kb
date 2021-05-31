from typing import List, Optional

from fastapi import APIRouter

from api import DB_CONNECT_STRING
from commitdb.postgres import PostgresCommitDB
from datamodel.commit import Commit

router = APIRouter(
    prefix="/commits",
    tags=["preprocessed_commits"],
    responses={404: {"description": "Not found"}},
)


# -----------------------------------------------------------------------------
@router.get("/{repository_url}", tags=["preprocessed_commits"])
async def get_commits(
    repository_url: str,
    commit_id: Optional[str] = None,
    details: Optional[bool] = False,
):
    db = PostgresCommitDB()
    db.connect(DB_CONNECT_STRING)
    commit = Commit(commit_id=commit_id, repository=repository_url)
    # use case: if a particular commit is queried, details should be returned
    if commit_id:
        details = True
    data = db.lookup_json(commit, details)

    return data


# -----------------------------------------------------------------------------
@router.post("/", tags=["preprocessed_commits"])
async def upload_preprocessed_commit(payload: List[Commit]):

    db = PostgresCommitDB()
    db.connect(DB_CONNECT_STRING)

    for commit in payload:
        db.save(commit)

    return {"status": "ok"}
