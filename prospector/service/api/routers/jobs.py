import redis
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from rq import Connection, Queue
from rq.job import Job

from backenddb.postgres import PostgresBackendDB
from data_sources.nvd.filter_entries import add_single_cve, process_entries
from data_sources.nvd.job_creation import (
    create_prospector_job,
    enqueue_jobs,
    run_prospector,
)
from log.logger import logger
from service.api.routers.nvd_feed_update import main
from util.config_parser import parse_config_file

config = parse_config_file()
redis_url = config.redis_url

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="service/static")


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


class DbJob(BaseModel):
    vuln_id: str | None = None
    repo: str | None = None
    version: str | None = None
    status: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    created_from: str | None = None
    results: str | None = None


@router.get("/{job_id}")
async def get_job(job_id: str):
    db = connect_to_db()
    job = db.lookup_job_id(job_id)
    db.disconnect()

    if job:
        response_object = {
            "job_data": {
                "job_id": job["_id"],
                "job_params": job["params"],
                "job_enqueued_at": job["enqueued_at"],
                "job_started_at": job["started_at"],
                "job_finished_at": job["finished_at"],
                "job_results": job["results"],
                "job_created_by": job["created_by"],
                "job_created_from": job["created_from"],
                "job_status": job["status"],
            }
        }
    else:
        response_object = {"message": "job not found"}
    return response_object


@router.get("/")
async def get_jobList():
    try:
        db = connect_to_db()
        joblist = db.get_all_jobs()
        db.disconnect()
    except Exception:
        logger.error(f"error updating the job list {joblist}", exc_info=True)
    return joblist


@router.post("/")
async def enqueue(job: DbJob):
    db = connect_to_db()
    if job.vuln_id:
        if job.created_from is None:
            # If the user pass only the vuln-id, make an API request to the NVD retrieving the info
            if job.repo is None or job.version is None:
                add_single_cve(job.vuln_id)
                process_entries()
                enqueue_jobs()
            else:  # all job info in request body, enqueue job with priority and save to db
                rq_job = create_prospector_job(
                    job.vuln_id, job.repo, job.version, at_front=True
                )
                logger.info("saving manual job in db", exc_info=True)
                db.save_manual_job(
                    rq_job.get_id(),
                    rq_job.args,
                    rq_job.created_at,
                    rq_job.started_at,
                    rq_job.ended_at,
                    rq_job.result,
                    "Manual",
                    rq_job.get_status(refresh=True),
                )
        else:  # job has a parent. Enqueue job and save to db with parent info
            rq_job = create_prospector_job(
                job.vuln_id, job.repo, job.version, at_front=True
            )
            logger.info("saving dependent job in db", exc_info=True)
            db.save_dependent_job(
                job.created_from,
                rq_job.get_id(),
                rq_job.args,
                rq_job.created_at,
                rq_job.started_at,
                rq_job.ended_at,
                rq_job.result,
                "Manual",
                rq_job.get_status(refresh=True),
            )
    else:
        logger.info("no vulnerability id provided", exc_info=True)

    db.disconnect()

    response_object = {
        "job_data": {
            "job_id": rq_job.get_id(),
            "job_status": rq_job.get_status(),
            "job_queue_position": rq_job.get_position(),
            "job_description": rq_job.description,
            "job_created_at": rq_job.created_at,
            "job_started_at": rq_job.started_at,
            "job_ended_at": rq_job.ended_at,
            "job_result": rq_job.result,
        }
    }

    return response_object


@router.put("/{job_id}")
async def update_job(job_id: str, job: DbJob):
    try:
        db = connect_to_db()
        db.update_job(
            job_id=job_id,
            status=job.status,
            started_at=job.started_at,
            ended_at=job.finished_at,
            results=job.results,
        )
        db.disconnect()
        response_object = {"message": "job updated"}
    except Exception:
        response_object = {"message": "error while updating job"}

    return response_object
