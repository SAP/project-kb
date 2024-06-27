import json
from datetime import datetime

from data_sources.nvd.job_creation import create_prospector_job
from evaluation.data_interaction import (
    load_multiple_cves,
    load_single_cve,
    save_multiple_cves,
    save_single_cve,
)
from util.report_analyzer import analyze_commit_relevance_results


# # Save CVE Data
# save_single_cve()
# # Load CVE Data
# cves = load_single_cve()

# save_multiple_cves()
cves = load_multiple_cves()

for cve in cves:
    print(cve["nvd_info"]["cve"]["id"])
    # print(cve)

# Send them to Prospector to run & save results to data_source/reports/<cve_id>
for cve in cves:
    res = create_prospector_job(
        repository_url=cve["repo_url"],
        cve_id=cve["nvd_info"]["cve"]["id"],
        report_type="json",
        version_interval=cve["version_interval"],
    )  # Creates .json files for each CVE in app/data_sources/reports
    # if res["job_data"]["job_status"]:
    #     reported_cves.append(cves["vulnerabilities"][0]["cve"]["id"])
