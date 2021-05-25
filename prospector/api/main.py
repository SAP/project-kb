import os

import uvicorn
from fastapi import FastAPI

# from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

# from .dependencies import oauth2_scheme
from api.routers import jobs, nvd, preprocessed, users
from commitdb.postgres import PostgresCommitDB
from datamodel.commit import Commit

# from pprint import pprint


DB_CONNECT_STRING = "postgresql://{}:{}@{}:{}/{}".format(
    os.environ["POSTGRES_USER"],
    os.environ["POSTGRES_PASSWORD"],
    os.environ["POSTGRES_HOST"],
    os.environ["POSTGRES_PORT"],
    os.environ["POSTGRES_DBNAME"],
).lower()

db = PostgresCommitDB()
db.connect(DB_CONNECT_STRING)

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
app.include_router(preprocessed.router)


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
# async def get_commits(repository_url, commit_id=None, token=Depends(oauth2_scheme)):
async def get_commits(repository_url, commit_id=None):
    commit = Commit(commit_id, repository_url)
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
    #         Click <a href="/docs">here</a> for docs and here for
    #         <a href="/openapi.json">OpenAPI specs</a>.
    #     </body>
    # </html>
    # """


# -----------------------------------------------------------------------------
@app.get("/status")
async def get_status():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
