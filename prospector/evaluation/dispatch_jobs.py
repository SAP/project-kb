import csv
import multiprocessing
import os

import redis
import requests
from dateutil.parser import isoparse
from rq import Connection, Queue
from rq.job import Job
from tqdm import tqdm

from core.prospector import prospector
from core.report import generate_report
from evaluation.utils import (
    INPUT_DATA_PATH,
    PROSPECTOR_REPORT_PATH,
    load_dataset,
    logger,
    config,
)
from llm.llm_service import LLMService

prospector_config = config.prospector_settings


def to_latex_table():
    data = load_dataset("results/scalco.csv")
    for e in data:
        print(f"{e[0]} & {e[1][19:]} & {e[5]} \\\\  \hline")  # noqa: W605


def run_prospector_and_generate_report(
    cve_id,
    version_interval,
    report_type: str,
    output_file,
    repository_url: str,
):
    """Call the prospector() and generate_report() functions. This also creates the LLMService singleton
    so that it is available in the context of the job.
    """
    params = {
        "vulnerability_id": cve_id,
        "repository_url": repository_url,
        "version_interval": version_interval,
        "use_backend": prospector_config.use_backend,
        "backend_address": prospector_config.backend,
        "git_cache": prospector_config.git_cache,
        "limit_candidates": prospector_config.max_candidates,
        "use_llm_repository_url": prospector_config.llm_service.use_llm_repository_url,
        "enabled_rules": prospector_config.enabled_rules,
    }

    if prospector_config.llm_service.use_llm_repository_url:
        try:
            LLMService(prospector_config.llm_service)
        except Exception as e:
            logger.debug(f"LLM Service could not be instantiated: {e}")
            raise e

    try:
        results, advisory_record = prospector(
            vulnerability_id=cve_id,
            repository_url=repository_url,
            version_interval=version_interval,
            backend_address=prospector_config.backend,
            enabled_rules=prospector_config.enabled_rules,
            git_cache=prospector_config.git_cache,
            use_llm_repository_url=prospector_config.llm_service.use_llm_repository_url,
        )
    except Exception as e:
        logger.debug(f"prospector() crashed: {e}")
        raise e

    logger.info(f"prospector() returned. Generating report now.")

    try:
        generate_report(
            results,
            advisory_record,
            report_type,
            output_file,
            prospector_params=params,
        )
    except Exception as e:
        logger.debug(f"Could not create report: {e}")
        raise e

    # return results, advisory_record
    return f"Ran Prospector on {cve_id}"


def dispatch_prospector_jobs(filename: str, selected_cves: str):
    """Dispatches jobs to the queue."""

    dataset = load_dataset(INPUT_DATA_PATH + filename + ".csv")
    # dataset = dataset[20:25]

    # Only run a subset of CVEs if the user supplied a selected set
    if len(selected_cves) != 0:
        dataset = [c for c in dataset if c[0] in selected_cves]

    logger.debug(f"Enabled rules: {prospector_config.enabled_rules}")

    dispatched_jobs = 0
    for cve in dataset:
        # Skip already existing reports
        if os.path.exists(f"{PROSPECTOR_REPORT_PATH}{filename}/{cve[0]}.json"):
            continue

        dispatched_jobs += 1

        # Send them to Prospector to run
        with Connection(redis.from_url(prospector_config.redis_url)):
            queue = Queue()

            job = Job.create(
                run_prospector_and_generate_report,
                kwargs={
                    "cve_id": cve[0],
                    "version_interval": cve[2],
                    "report_type": "json",
                    "output_file": f"{PROSPECTOR_REPORT_PATH}{filename}/{cve[0]}.json",
                    "repository_url": (
                        cve[1]
                        if not prospector_config.llm_service.use_llm_repository_url
                        else None
                    ),
                },
                description="Prospector Job",
                id=cve[0],
            )

            queue.enqueue_job(job)

        # print(f"Dispatched job {cve[0]} to queue.") # Sanity Check

    print(f"Dispatched {dispatched_jobs} jobs.")


def empty_queue():
    with Connection(redis.from_url(prospector_config.redis_url)):
        queue = Queue("default")

        queue.empty()

        print("Emptied the queue.")
