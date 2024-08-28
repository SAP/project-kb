import os

import redis
from rq import Connection, Queue
from rq.job import Job

from core.prospector import prospector
from core.report import generate_report
from data_sources.nvd.filter_entries import (
    process_entries,
    retrieve_vulns,
    save_vuln_to_db,
)
from data_sources.nvd.job_creation import (
    create_prospector_job,
    run_prospector,
)
from evaluation.create_jobs import _create_prospector_job, enqueue_jobs
from evaluation.utils import (
    INPUT_DATA_PATH,
    PROSPECTOR_REPORTS_PATH_HOST,
    PROSPECTOR_REPORTS_PATH_CONTAINER,
    load_dataset,
    logger,
    config,
)
from llm.llm_service import LLMService

prospector_config = config.prospector_settings


def dispatch_prospector_jobs(filename: str, selected_cves: str):
    """Dispatches jobs to the queue."""

    dataset = load_dataset(INPUT_DATA_PATH + filename + ".csv")
    # dataset = dataset[200:300]  # done 0-100,

    # Only run a subset of CVEs if the user supplied a selected set
    if len(selected_cves) != 0:
        dataset = [c for c in dataset if c[0] in selected_cves]

    logger.debug(f"Enabled rules: {prospector_config.enabled_rules}")
    logger.info(f"Prospector settings: {prospector_config.enabled_rules}")

    dispatched_jobs = 0
    for cve in dataset:
        # Skip already existing reports
        if os.path.exists(f"{PROSPECTOR_REPORTS_PATH_HOST}/{cve[0]}.json"):
            continue

        dispatched_jobs += 1

        # Send them to Prospector to run
        with Connection(redis.from_url(prospector_config.redis_url)):
            queue = Queue(default_timeout=3600)

            job = Job.create(
                _run_prospector_and_generate_report,
                kwargs={
                    "cve_id": cve[0],
                    "version_interval": (
                        cve[2] if config.version_interval else "None:None"
                    ),
                    "report_type": "json",
                    "output_file": f"{PROSPECTOR_REPORTS_PATH_CONTAINER}{cve[0]}.json",
                    "repository_url": cve[1],
                },
                description="Prospector Job",
                id=cve[0],
            )

            queue.enqueue_job(job)

    logger.info(f"Dispatched {dispatched_jobs} jobs.")
    print(f"Dispatched {dispatched_jobs} jobs.")


def _run_prospector_and_generate_report(
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
        "use_llm_repository_url": False,
        "enabled_rules": prospector_config.enabled_rules,
    }

    if prospector_config.llm_service.use_llm_repository_url:
        try:
            LLMService(prospector_config.llm_service)
        except Exception as e:
            logger.error(f"LLM Service could not be instantiated: {e}")
            raise e

    try:
        results, advisory_record = prospector(**params)
    except Exception as e:
        logger.error(f"prospector() crashed at {cve_id}: {e}")
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
        logger.error(f"Could not create report: {e}")
        raise e

    # return results, advisory_record
    return f"Ran Prospector on {cve_id}"


def empty_queue():
    """Remove all jobs from the queue. Attention: this does not stop jobs that
    are currently executing."""
    with Connection(redis.from_url(prospector_config.redis_url)):
        queue = Queue("default")

        queue.empty()

        print("Emptied the queue.")


async def dispatch_jobs_with_api(filename: str, selected_cves: str):
    """Dispatches jobs to the queue."""
    # Retrieve CVE data
    cve_data = await retrieve_vulns(10)

    # Save raw CVE data to the database
    save_vuln_to_db(cve_data)

    # Process and filter the new CVE data and save results to the database
    processed_vulns = await process_entries()

    print("CVEs ready to be enqueued.")

    # Enqueue jobs for new processed CVEs
    await enqueue_jobs()


def start():
    # vuln_id = "CVE-2018-14840"
    # repo_url = "https://github.com/intelliants/subrion"
    # v_int = "4.2.1:4.2.2"
    vuln_id = "CVE-2010-0156"
    repo_url = "https://github.com/puppetlabs/puppet"
    v_int = "0.25.1:0.25.2"
    _create_prospector_job(vuln_id, repo_url, v_int)
