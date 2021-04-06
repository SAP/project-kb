import os
from sys import argv
from fastapi import APIRouter, Depends, HTTPException

import redis
from rq import Queue, Connection
from rq.job import Job

from git.git import do_clone

from api.routers.nvd_feed_update import main

from ..dependencies import (
    get_current_active_user,
    fake_users_db,
    fake_hash_password,
    User,
    UserInDB,
    oauth2_scheme,
)

# from fastapi.security import OAuth2PasswordRequestForm

redis_url = os.environ["REDIS_URL"]

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)

# -----------------------------------------------------------------------------
#
@router.post("/clone", tags=["jobs"])
async def create_clone_job(repository):
    with Connection(redis.from_url(redis_url)):
        q = Queue()
        job = Job.create(
            do_clone,
            (repository, "/tmp",),
            description="clone job " + repository,
            result_ttl=1000,
        )
        q.enqueue_job(job)

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
        q = Queue()
        job = q.fetch_job(job_id)
    if job:
        print("job {} result: {}".format(job.get_id(), job.result))
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
        q = Queue()
        job = Job.create(main, description="update nvd feed", result_ttl=1000,)
        q.enqueue_job(job)

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
