import json
import sys

import redis
from rq import Connection, Queue
from rq.job import Job

from core.prospector import prospector
from core.report import generate_report
from util.config_parser import parse_config_file

# get the redis server url
config = parse_config_file()
# redis_url = config.redis_url
backend = config.backend

redis_url = "redis://localhost:6379/0"
print("redis url: ", redis_url)
print("redis url: ", backend)


def run_prospector(vuln_id, repo_url, v_int):
    results, advisory_record = prospector(
        vulnerability_id=vuln_id,
        repository_url=repo_url,
        version_interval=v_int,
        backend_address=backend,
    )
    generate_report(
        results,
        advisory_record,
        "html",
        f"data_sources/reports/{vuln_id}",
    )

    return results, advisory_record


def create_prospector_job(entry):
    # data = json.loads(entry)

    id = entry["nvd_info"]["cve"]["id"]
    repo = entry["repo_url"]
    version = entry["version_interval"]

    with Connection(redis.from_url(redis_url)):
        queue = Queue()

        job = Job.create(
            run_prospector,
            args=(id, repo, version),
            description="prospector job",
            id=id,
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
