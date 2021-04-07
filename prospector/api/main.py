import os
from pprint import pprint

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from commitdb.postgres import PostgresCommitDB

from .dependencies import (
    User,
    UserInDB,
    fake_hash_password,
    fake_users_db,
    get_current_active_user,
    oauth2_scheme,
)
from .routers import jobs, nvd, users

db_pass = os.environ["POSTGRES_PASSWORD"]
connect_string = "HOST=localhost;DB=postgres;UID=postgres;PWD={};PORT=5432;".format(
    db_pass
)

db = PostgresCommitDB()
db.connect(connect_string)

api_metadata = [
    {"name": "data", "description": "Operations with data used to train ML models."},
    {
        "name": "jobs",
        "description": "Manage jobs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

app = FastAPI(openapi_tags=api_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(nvd.router)

# -----------------------------------------------------------------------------
# Data here refers to training data, used to train ML models
# TODO find a less generic term
@app.get("/data", tags=["data"])
async def get_data():
    return [
        {
            "repository_url": "https://github.com/apache/struts",
            "commit_id": "a4612fe8232678cab3297",
            "label": 1,
            "vulnerability_id": "CVE-XXXX-YYYY",
        },
        {
            "repository_url": "https://github.com/apache/struts",
            "commit_id": "a4612fe8232678cab3297",
            "label": 1,
            "vulnerability_id": "CVE-XXXX-YYYY",
        },
        {
            "repository_url": "https://github.com/apache/struts",
            "commit_id": "a4612fe8232678cab3297",
            "label": 1,
            "vulnerability_id": "CVE-XXXX-YYYY",
        },
    ]


@app.post("/data", tags=["data"])
async def create_data(repository_url, commit_id, label, vulnerability_id):
    return {
        "repository_url": repository_url,
        "commit_id": commit_id,
        "label": label,
        "vulnerability_id": vulnerability_id,
    }


# -----------------------------------------------------------------------------
@app.get("/commits/{repository_url}")
async def get_commits(repository_url, commit_id=None, token=Depends(oauth2_scheme)):
    commit = (commit_id, repository_url)
    data = db.lookup(commit)

    return data


# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_items():
    response = RedirectResponse(url="/docs")
    return response
    # return """
    # <html>
    #     <head>
    #         <title>Prospector</title>
    #     </head>
    #     <body>
    #         <h1>Prospector API</h1>
    #         Click <a href="/docs">here</a> for docs and here for <a href="/openapi.json">OpenAPI specs</a>.
    #     </body>
    # </html>
    # """


# -----------------------------------------------------------------------------
@app.get("/status")
async def get_status():
    status = {"status": "ok"}
    return status
