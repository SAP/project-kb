from typing import List, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api import DB_CONNECT_STRING
from commitdb.postgres import PostgresCommitDB
from datamodel.commit import Commit

router = APIRouter(
    prefix="/commits",
    tags=["commits"],
    responses={404: {"description": "Not found"}},
)


# -----------------------------------------------------------------------------
@router.get("/{repository_url:path}")
async def get_commits(
    repository_url: str,
    commit_id: Optional[str] = None,
):
    db = PostgresCommitDB()
    db.connect(DB_CONNECT_STRING)
    # use case: if a particular commit is queried, details should be returned
    data = db.lookup(repository_url, commit_id)
    res = []
    if len(data):
        for d in data:
            if d:
                res.append(d.dict())
            else:
                res.append(None)
    return JSONResponse(res)


# -----------------------------------------------------------------------------
@router.post("/")
async def upload_preprocessed_commit(payload: List[Commit]):

    db = PostgresCommitDB()
    db.connect(DB_CONNECT_STRING)

    for commit in payload:
        db.save(commit)

    return {"status": "ok"}
