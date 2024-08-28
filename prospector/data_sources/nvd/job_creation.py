import json
import sys
import time
from datetime import datetime

import redis
import requests
from rq import Connection, Queue, get_current_job

from backenddb.postgres import PostgresBackendDB
from core.prospector import prospector
from core.report import generate_report
from log.logger import logger
from util.config_parser import parse_config_file

# get the redis server url and backend from configuration file
config = parse_config_file()
# redis_url = config.redis_url
# backend = config.backend
redis_url = "redis://localhost:6379/0"
backend = "http://backend:8000"


def run_prospector(vuln_id, repo_url, v_int):
    job = get_current_job()
    job_id = job.get_id()
    url = f"{backend}/jobs/{job_id}"
    data = {
        "status": job.get_status(),
        "started_at": job.started_at.isoformat(),
    }

    try:
        response = requests.put(url, json=data)
        if response.status_code == 200:
            response_object = response.json()
            print(response_object)
        else:
            print("Error:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

    params = {
        "vulnerability_id": vuln_id,
        "repository_url": repo_url,
        "version_interval": v_int,
        "use_backend": True,
        "backend_address": backend,
        "git_cache": "/tmp/gitcache",
        "limit_candidates": 2000,
        "use_llm_repository_url": False,
        "enabled_rules": config.enabled_rules,
    }
    try:
        results, advisory_record = prospector(**params)
        generate_report(
            results,
            advisory_record,
            "html",
            f"data_sources/reports/{vuln_id}_{job_id}",
        )
        status = "finished"
        results = f"data_sources/reports/{vuln_id}_{job_id}"
    except Exception as e:
        status = "failed"
        results = None
        logger.error(f"job failed during execution: {e}")
    finally:
        end_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        print(job_id, status, end_time, results)
        data = {"status": status, "finished_at": end_time, "results": results}
        try:
            response = requests.put(url, json=data)
            if response.status_code == 200:
                response_object = response.json()
                print(response_object)
            else:
                print("Error:", response.status_code)
        except requests.exceptions.RequestException as e:
            print("Error:", e)

    return f"data_sources/reports/{vuln_id}_{job_id}"


def create_prospector_job(vuln_id, repo, version, at_front=False):
    with Connection(redis.from_url(redis_url)):
        queue = Queue(default_timeout=800)
        if at_front:
            job = queue.enqueue(
                run_prospector, args=(vuln_id, repo, version), at_front=True
            )
        else:
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
            logger.error(
                "error while creating automatically the jobs", exc_info=True
            )

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
            logger.error(
                "error while saving automatically the jobs", exc_info=True
            )

    db.disconnect()
