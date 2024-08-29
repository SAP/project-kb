import os
from datetime import datetime

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from backenddb.postgres import PostgresBackendDB
from log.logger import logger
from pipeline import filter_entries, job_creation
from util.config_parser import parse_config_file

router = APIRouter(
    prefix="/feeds",
    tags=["feeds"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="service/static")

config = parse_config_file()
redis_url = config.redis_url


def connect_to_db():
    db = PostgresBackendDB(
        config.database.user,
        config.database.password,
        config.database.host,
        config.database.port,
        config.database.dbname,
    )
    db.connect()
    return db


@router.get("/reports")
async def get_reports(request: Request):
    report_list = []
    for filename in os.listdir("/app/data_sources/reports"):
        if filename.endswith(".html"):
            file_path = os.path.join("/app/data_sources/reports", filename)
            mtime = os.path.getmtime(file_path)
            mtime_dt = datetime.fromtimestamp(mtime)
            report_list.append((os.path.splitext(filename)[0], mtime_dt))
            report_list.sort(key=lambda x: x[1], reverse=True)
    return templates.TemplateResponse(
        "report_list.html", {"request": request, "report_list": report_list}
    )


@router.get("/{vuln_id}")
async def get_vuln(vuln_id: str):

    db = connect_to_db()
    vuln = db.lookup_vuln(vuln_id)
    db.disconnect()

    if vuln:
        response_object = {
            "vuln_data": {
                "vuln_id": vuln["vuln_id"],
                "vuln_pubdate": vuln["published_date"],
                "vuln_lastmoddate": vuln["last_modified_date"],
                "vuln_raw_record": vuln["raw_record"],
                "vuln_source": vuln["source"],
                "vuln_url": vuln["url"],
                "vuln_alias": vuln["alias"],
            }
        }
    else:
        response_object = {"message": "vulnerability not found"}
    return response_object


@router.get("/")
async def get_vulnList():
    try:
        db = connect_to_db()
        vulnlist = db.lookup_vulnList()
        db.disconnect()
    except Exception:
        logger.error("error updating the vuln list", exc_info=True)
    return vulnlist


@router.get("/fetch_vulns/{d_time}")
async def get_vulns(d_time: int):
    # Retrieve and save new vulns using NVD APIs
    try:
        await filter_entries.retrieve_vulns(d_time)
        response_object = {"message": "success"}
    except Exception:
        response_object = {
            "message": "error while retrieving new vulnerabilities"
        }
    return response_object


@router.post("/process_vulns")
async def get_process_vulns():
    # Process entries and save into db
    try:
        await filter_entries.process_entries()
        response_object = {"message": "success"}
    except Exception:
        logger.error("error while processing vulnerabilities", exc_info=True)
        response_object = {"message": "error while processing vulnerabilities"}
    return response_object


@router.post("/create_jobs")
async def create_jobs():
    # Create and enqueue the jobs. Save them into db
    try:
        await job_creation.enqueue_jobs()
        response_object = {"message": "success"}
    except Exception:
        logger.error("Error while creating jobs", exc_info=True)
        logger.error(f"{redis_url}")
        response_object = {"message": "error while creating jobs"}
    return response_object
