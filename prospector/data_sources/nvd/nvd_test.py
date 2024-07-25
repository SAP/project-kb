from data_sources.nvd.filter_entries import (
    process_entries,
    retrieve_vulns,
    save_vuln_to_db,
)
from data_sources.nvd.job_creation import enqueue_jobs

# request new cves entries through NVD API and save to db
cve_data = retrieve_vulns(7)

# save to db
save_vuln_to_db(cve_data)


"""with open("filtered_cves.json", "w") as outfile:
    json.dump(filtered_cves, outfile)"""

print("retrieved cves")
# print(cves)

# get entry from db and process
processed_vulns = process_entries()
print("ready to be enqueued: ")
print(processed_vulns)

# if processed_vulns:
#    for entry in processed_vulns:
#        job_info = create_prospector_job(entry)
#        save_job_to_db(job_info)

enqueue_jobs()
