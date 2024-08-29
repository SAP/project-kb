import asyncio
from pipeline.filter_entries import (
    get_cve_data,
    process_cve_data,
    save_cves_to_db,
)
from pipeline.job_creation import enqueue_jobs


DAYS_AGO = 10  # Time period from DAYS_AGO to now to retrieve CVEs from NVD


async def dispatch_jobs():
    """Gets CVEs from the last X days, filters them and enqueues them in the
    Queue. Workers fetch the jobs and execute the Prospector function on them.
    """
    # Retrieve the CVE data
    cve_data = await get_cve_data(DAYS_AGO)

    # Save data to the vulnerabilities table in the database
    save_cves_to_db(cve_data)

    # get entry from db and process
    processed_cves = await process_cve_data()

    await enqueue_jobs(reports_filepath="pipeline/reports/")


async def main():
    """Starting point to enqueue jobs into the pipeline"""
    await dispatch_jobs()


if __name__ == "__main__":
    asyncio.run(main())
