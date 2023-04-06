from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from commitdb.postgres import PostgresCommitDB
from util.config_parser import parse_config_file

config = parse_config_file()


router = APIRouter(
    prefix="/commits",
    tags=["commits"],
    responses={404: {"description": "Not found"}},
)


# -----------------------------------------------------------------------------
@router.get("/{repository_url:path}", status_code=200)
async def get_commits(
    repository_url: str,
    commit_id: Optional[str] = None,
):
    db = PostgresCommitDB(
        config.database.user,
        config.database.password,
        config.database.host,
        config.database.port,
        config.database.dbname,
    )
    db.connect()
    data = db.lookup(repository_url, commit_id)

    if len(data) == 0:
        raise HTTPException(status_code=404, detail="Commit not found")

    return JSONResponse(data)


# -----------------------------------------------------------------------------
@router.post("/")
async def upload_preprocessed_commit(payload: List[Dict[str, Any]]):

    db = PostgresCommitDB(
        config.database.user,
        config.database.password,
        config.database.host,
        config.database.port,
        config.database.dbname,
    )
    db.connect()

    for commit in payload:
        db.save(commit)

    return {"status": "ok"}
