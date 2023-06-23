import json
import sys
import time
from datetime import datetime, timedelta

import redis
from rq import Connection, Queue, get_current_job

from backenddb.postgres import PostgresBackendDB
from core.prospector import prospector
from core.report import generate_report
from log.logger import logger
from util.config_parser import parse_config_file

# get the redis server url
config = parse_config_file()
redis_url = config.redis_url
backend = config.backend


def run_prospector(vuln_id, repo_url, v_int):

    start_time = time.time()
    job = get_current_job()
    db = connect_to_db()
    db.update_job(job.get_id(), job.get_status(), job.started_at)

    try:
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
    except Exception:
        end_time = time.time()
        elapsed_time = end_time - start_time
        ended_at = job.started_at + timedelta(seconds=int(elapsed_time))
        logger.error("job failed during execution")
        print(job.get_id(), "failed", ended_at)
        db.update_job(job.get_id(), "failed", ended_at=ended_at)
        db.disconnect()
    else:
        end_time = time.time()
        elapsed_time = end_time - start_time
        ended_at = job.started_at + timedelta(seconds=int(elapsed_time))
        print(job.get_id(), "finished", ended_at, f"data_sources/reports/{vuln_id}")
        db.update_job(
            job.get_id(),
            "finished",
            ended_at=ended_at,
            results=f"data_sources/reports/{vuln_id}",
        )
        db.disconnect()

    return f"data_sources/reports/{vuln_id}"


def create_prospector_job(vuln_id, repo, version):
    with Connection(redis.from_url(redis_url)):
        queue = Queue(default_timeout=500)
        job = queue.enqueue(run_prospector, args=(vuln_id, repo, version))

    return job


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


async def enqueue_jobs():
    db = connect_to_db()
    processed_vulns = db.get_processed_vulns_not_in_job()
    print(processed_vulns)
    created_by = "Auto"
    for processed_vuln in processed_vulns:
        pv_id = processed_vuln["_id"]
        pv_repository = processed_vuln["repository"]
        pv_versions = processed_vuln["versions"]
        v_vuln_id = processed_vuln["vuln_id"]

        try:
            job = create_prospector_job(v_vuln_id, pv_repository, pv_versions)
        except Exception:
            logger.error("error while creating automatically the jobs", exc_info=True)

        try:
            db.save_job(
                job.get_id(),
                pv_id,
                job.args,
                job.created_at,
                job.started_at,
                job.ended_at,
                job.result,
                created_by,
                job.get_status(refresh=True),
            )
        except Exception:
            logger.error("error while saving automatically the jobs", exc_info=True)

    db.disconnect()
