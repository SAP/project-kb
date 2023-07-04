import uvicorn

# from .dependencies import oauth2_scheme
from api.routers import feeds, jobs, nvd, preprocessed, users
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from log.logger import logger
from util.config_parser import parse_config_file

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
app.include_router(nvd.router)
app.include_router(preprocessed.router)
app.include_router(feeds.router)
app.include_router(jobs.router)

app.mount("/static", StaticFiles(directory="service/static"), name="static")
app.mount("/reports", StaticFiles(directory="./data_sources/reports"), name="reports")


# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_index():
    response = RedirectResponse(url="static/feed.html")
    return response


# -----------------------------------------------------------------------------
@app.get("/status")
async def get_status():
    return {"status": "ok"}


if __name__ == "__main__":
    config = parse_config_file()
    logger.setLevel(config.log_level)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
