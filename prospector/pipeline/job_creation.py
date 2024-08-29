import json
import sys
import time
from datetime import datetime
from typing import Optional

import redis
import requests
from rq import Connection, Queue, get_current_job

from backenddb.postgres import PostgresBackendDB
from cli.console import ConsoleWriter, MessageStatus
from core.prospector import prospector
from core.report import generate_report
from llm.llm_service import LLMService
from log.logger import logger
from util.config_parser import parse_config_file

# get the redis server url and backend from configuration file
config = parse_config_file()
redis_url = config.redis_url
backend = config.backend


def create_prospector_job(
    vuln_id: str,
    repo: Optional[str],
    version: str,
    report_filepath: str,
    at_front=False,
):
    """Creates a job with the Prospector function for the given vulnerability,
    optionally at the front of the queue.

    Params:
        vuln_id (str): The ID of the CVE.
        repo (str): The URL of the affected repository.
        version (str): The extracted version interval.
        reports_filepath (str): The filepath where the report will be saved.
        at_front (bool): Enqueue job at the front of the queue.

    Returns: The object of the created job.
    """

    with Connection(redis.from_url(redis_url)):
        queue = Queue(default_timeout=800)
        if at_front:
            job = queue.enqueue(
                _run_prospector,
                args=(vuln_id, repo, version, report_filepath),
                at_front=True,
            )
        else:
            job = queue.enqueue(
                _run_prospector, args=(vuln_id, repo, version, report_filepath)
            )

    return job


def _run_prospector(
    cve_id: str,
    repository_url: Optional[str],
    version_interval: str,
    report_filepath: str,
):
    """Call the prospector() and generate_report() functions. This also creates
    the LLMService singleton so that it is available in the context of the job.

    Returns: The filepath of the created report on the host.
    """

    job = get_current_job()
    job_id = job.get_id()

    url = f"{backend}/jobs/{job_id}"
    data = {
        "status": job.get_status(),
        "started_at": job.started_at.isoformat(),
    }

    # Update the database with the new job status
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
        "vulnerability_id": cve_id,
        "repository_url": repository_url,
        "version_interval": version_interval,
        "use_backend": config.use_backend,
        "backend_address": config.backend,
        "git_cache": config.git_cache,
        "limit_candidates": config.max_candidates,
        "use_llm_repository_url": config.use_llm_repository_url,
        "enabled_rules": config.enabled_rules,
    }

    if config.llm_service.use_llm_repository_url:
        try:
            LLMService(config.llm_service)
        except Exception as e:
            logger.error(f"LLM Service could not be instantiated: {e}")
            raise e

    # Execute the Prospector function
    try:
        results, advisory_record = prospector(**params)

        generate_report(
            results,
            advisory_record,
            "html",
            f"{report_filepath}{cve_id}_{job_id}",
        )
        status = "finished"
        results = (f"{report_filepath}{cve_id}_{job_id}",)

    except Exception as e:
        status = "failed"
        results = None
        logger.error(f"Job {cve_id} failed during execution: {e}")

    finally:
        end_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

        ConsoleWriter.print(
            f"{job_id} {status} at {end_time}. Report saved in {results}"
        )

        # Update job in database
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

    return (f"{report_filepath}{cve_id}_{job_id}",)


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


async def enqueue_jobs(reports_filepath: str, creator: str = "Auto"):
    """Creates jobs for each processed vulnerability that has not yet been
    processed.

    Params:
        creator (str): The creator of the jobs, eg. Auto

    """
    with ConsoleWriter("Enqueueing Jobs") as console:
        db = connect_to_db()
        processed_cves = db.get_processed_vulns_not_in_job()

        console.print(
            f"Enqueueing {len(processed_cves)} jobs for {[cve_entry['vuln_id'] for cve_entry in processed_cves]}",
            status=MessageStatus.OK,
        )

        for processed_vuln in processed_cves:
            pv_id = processed_vuln["_id"]
            pv_repository = processed_vuln["repository"]
            pv_versions = processed_vuln["versions"]
            v_vuln_id = processed_vuln["vuln_id"]

            try:
                job = create_prospector_job(
                    v_vuln_id, pv_repository, pv_versions, reports_filepath
                )
            except Exception:
                logger.error(
                    "Error when creating jobs for processed vulnerabilities",
                    exc_info=True,
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
                    creator,
                    job.get_status(refresh=True),
                )
            except Exception:
                logger.error(
                    "Error when saving the created job to the database.",
                    exc_info=True,
                )

        db.disconnect()

        console.print(
            f"\n\t\tEnqueueing finished",
            status=MessageStatus.OK,
        )
