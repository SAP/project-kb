import json
import sys

import redis
from rq import Connection, Queue
from rq.job import Job

from commitdb.postgres import PostgresCommitDB
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


# def create_prospector_job(entry):
#    # data = json.loads(entry)
#
#    id = entry["nvd_info"]["cve"]["id"]
#    repo = entry["repo_url"]
#    version = entry["version_interval"]
#
#    with Connection(redis.from_url(redis_url)):
#        queue = Queue(default_timeout=300)
#
#        job = Job.create(
#            run_prospector,
#            args=(id, repo, version),
#            description="prospector job",
#            id=id,
#        )
#        queue.enqueue_job(job)
#
#    #response_object = {
#    #    "job_data": {
#    #        "job_id": job.get_id(),
#    #        "job_status": job.get_status(),
#    #        "job_queue_position": job.get_position(),
#    #        "job_description": job.description,
#    #        "job_enqueued_at": job.created_at,
#    #        "job_started_at": job.started_at,
#    #        "job_finished_at": job.ended_at,
#    #        "job_result": job.result,
#    #        "job_args": job.args
#    #    }
#    #}
#    return job
#


def create_prospector_job(vuln_id, repo, version):

    with Connection(redis.from_url(redis_url)):
        queue = Queue(default_timeout=500)

        job = Job.create(
            run_prospector,
            args=(vuln_id, repo, version),
            description="prospector job",
            id=vuln_id,
        )
        queue.enqueue_job(job)
    return job


def connect_to_db():
    db = PostgresCommitDB(
        config.database.user,
        config.database.password,
        config.database.host,
        config.database.port,
        config.database.dbname,
    )
    db.connect()
    return db


def disconnect_from_database(db):
    db.disconnect()


# def save_job_to_db(job):
#    db = connect_to_db()
#    results=""
#    created_from="Auto"
#    processed_vulns = db.lookup_processed_no_job()
#    pv_id=processed_vulns[0]
#
#
#
#
#    db.save_job(job.get_id(),pv_id,job.args,job.created_at,job.started_at,job.ended_at,job.result,job.origin,created_from, job.get_status(refresh=True))
#
#    db.disconnect()


# separate job creation task
# retrieve processed vulns and cve_id,
# save_job using id from retrieved processed vulns
def enqueue_jobs():
    db = connect_to_db()
    processed_vulns = db.get_processed_vulns_not_in_job()
    print(processed_vulns)
    created_from = "Auto"
    for processed_vuln in processed_vulns:
        pv_id = processed_vuln[0]
        pv_repository = processed_vuln[1]
        pv_versions = processed_vuln[2]
        v_vuln_id = processed_vuln[3]

        job = create_prospector_job(v_vuln_id, pv_repository, pv_versions)

        db.save_job(
            job.get_id(),
            pv_id,
            job.args,
            job.created_at,
            job.started_at,
            job.ended_at,
            job.result,
            job.origin,
            created_from,
            job.get_status(refresh=True),
        )

    db.disconnect()
