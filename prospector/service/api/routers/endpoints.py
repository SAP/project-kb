import os
import sys
from datetime import datetime

import redis
from api.rq_utils import get_all_jobs, queue
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from rq import Connection, Queue
from rq.job import Job
from starlette.responses import RedirectResponse

from data_sources.nvd.job_creation import run_prospector
from util.config_parser import parse_config_file

# from core.report import generate_report

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="service/static")


config = parse_config_file()


redis_url = config.redis_url
print("redis url: ", redis_url)


async def redirect(url):
    response = RedirectResponse(url)
    return response


# endpoint for deleting a job
@router.get("/delete/{job_id}", tags=["jobs"])
async def delete_job(job_id):
    with Connection(redis.from_url(redis_url)):
        queue = Queue()
        job = queue.fetch_job(job_id)
    if job:
        job.delete()
        response_object = {"message": "job deleted"}
    else:
        response_object = {"message": "job not found"}
    # redirect to job list page
    return response_object


# endpoint for getting the job report
@router.get("/get_report/{job_id}", tags=["jobs"])
async def get_report(job_id):
    html_report = None
    # with Connection(redis.from_url(redis_url)):
    # queue = Queue()
    # job = queue.fetch_job(job_id)
    # get and redirect to the html page of the generated report
    with open(
        f"/app/data_sources/reports/{job_id}.html",
        "r",
    ) as f:
        html_report = f.read()
    return HTMLResponse(content=html_report, status_code=200)


# endpoint for opening the settings page of the selected job
@router.get("/get_settings/{job_id}", tags=["jobs"], response_class=HTMLResponse)
async def get_settings(job_id, request: Request):
    with Connection(redis.from_url(redis_url)):
        queue = Queue()
        job = queue.fetch_job(job_id)
    if job:
        return templates.TemplateResponse(
            "job_configuration.html", {"request": request, "job": job}
        )
    else:
        return {"message": "job not found"}


@router.get("/report_page", response_class=HTMLResponse)
async def report_page(request: Request):
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


# endpoint for getting a job
@router.get("/get_job/{job_id}", tags=["jobs"])
async def get_status(job_id):
    # get job from connected redis queue
    job = queue.fetch_job(job_id)
    # process returned job and prepare response
    if job:
        response_object = {
            "status": "success",
            "data": {
                "job_id": job.get_id(),
                "job_status": job.get_status(),
                "job_result": job.result,
            },
        }
        status_code = 200
    else:
        response_object = {"message": "job not found"}
        status_code = 500
    return response_object, status_code


# endpoint for enqueuing a prospector job given cve, repository and version interval
@router.get("/enqueue/", tags=["jobs"])
async def enqueue_job(cve: str, repo: str, version: str):
    with Connection(redis.from_url(redis_url)):
        queue = Queue()
        job = Job.create(
            run_prospector,
            args=(cve, repo, version),
            description="prospector",
            id=cve,
        )
        queue.enqueue_job(job)

    response_object = {
        "job_data": {
            "job_id": job.get_id(),
            "job_status": job.get_status(),
            "job_queue_position": job.get_position(),
            "job_description": job.description,
            "job_created_at": job.created_at,
            "job_started_at": job.started_at,
            "job_ended_at": job.ended_at,
            "job_result": job.result,
        }
    }
    return response_object


"""@router.get("/enqueue_job/", tags=["jobs"])
async def enqueue_job(cve: str, repo: str, version_interval: str):
    parameters = [
        "client/cli/main.py",
        "CVE-2014-0050",
        "--repository",
        "https://github.com/apache/commons-fileupload",
        "--version-interval",
        "FILEUPLOAD_1_3:FILEUPLOAD_1_3_1",
    ]

    with Connection(redis.from_url(redis_url)):
        queue = Queue()
        job = Job.create(main, [parameters], description="prospector")
        queue.enqueue_job(job)

    response_object = {
        "job_data": {
            "job_id": job.get_id(),
            "job_status": job.get_status(),
            "job_queue_position": job.get_position(),
            "job_description": job.description,
            "job_created_at": job.created_at,
            "job_started_at": job.started_at,
            "job_ended_at": job.ended_at,
            "job_result": job.result,
        }
    }
    return await redirect("/jobs/home")
"""
