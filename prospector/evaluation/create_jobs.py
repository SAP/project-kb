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
from llm.llm_service import LLMService
from log.logger import logger
from util.config_parser import parse_config_file

from evaluation.utils import (
    PROSPECTOR_REPORTS_PATH_CONTAINER,
    logger,
    config,
)

prospector_config = config.prospector_settings


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
            job = _create_prospector_job(v_vuln_id, pv_repository, pv_versions)
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


def _create_prospector_job(vuln_id, repo, version, at_front=False):
    with Connection(redis.from_url(prospector_config.redis_url)):
        queue = Queue(default_timeout=800)
        if at_front:
            job = queue.enqueue(
                _run_prospector_and_generate_report,
                args=(vuln_id, repo, version),
                at_front=True,
            )
        else:
            job = queue.enqueue(
                _run_prospector_and_generate_report,
                args=(vuln_id, repo, version),
            )

    return job


def _run_prospector_and_generate_report(vuln_id, repo_url, v_int):
    job = get_current_job()
    job_id = job.get_id()
    url = f"{prospector_config.backend}/jobs/{job_id}"
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
        "backend_address": prospector_config.backend,
        "git_cache": "/tmp/gitcache",
        "limit_candidates": 2000,
        "use_llm_repository_url": False,
        "enabled_rules": prospector_config.enabled_rules,
    }

    try:
        LLMService(prospector_config.llm_service)
    except Exception as e:
        logger.error(f"LLM Service could not be instantiated: {e}")
        raise e

    try:
        results, advisory_record = prospector(**params)
        generate_report(
            results,
            advisory_record,
            "json",
            f"{PROSPECTOR_REPORTS_PATH_CONTAINER}{vuln_id}.json",
            prospector_params=params,
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


def connect_to_db():
    db = PostgresBackendDB(
        prospector_config.database.user,
        prospector_config.database.password,
        prospector_config.database.host,
        prospector_config.database.port,
        prospector_config.database.dbname,
    )
    db.connect()
    return db
