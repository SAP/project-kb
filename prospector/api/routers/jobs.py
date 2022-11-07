import os

import redis
from fastapi import APIRouter
from rq import Connection, Queue
from rq.job import Job

from api.routers.nvd_feed_update import main
from git.git import do_clone
from log.logger import logger

redis_url = os.environ["REDIS_URL"]

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}},
)


# -----------------------------------------------------------------------------
@router.post("/clone", tags=["jobs"])
async def create_clone_job(repository):
    with Connection(redis.from_url(redis_url)):
        queue = Queue()
        job = Job.create(
            do_clone,
            (
                repository,
                "/tmp",
            ),
            description="clone job " + repository,
            result_ttl=1000,
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


@router.get("/{job_id}", tags=["jobs"])
async def get_job(job_id):
    with Connection(redis.from_url(redis_url)):
        queue = Queue()
        job = queue.fetch_job(job_id)
    if job:
        logger.info("job {} result: {}".format(job.get_id(), job.result))
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
    else:
        response_object = {"status": "error"}
    return response_object


@router.post("/update_feed", tags=["jobs"])
async def create_update_feed_job():
    with Connection(redis.from_url(redis_url)):
        queue = Queue()
        job = Job.create(
            main,
            description="update nvd feed",
            result_ttl=1000,
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
