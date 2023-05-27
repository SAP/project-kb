from filter_entries import find_matching_entries_test, get_cves
from job_creation import create_prospector_job

# request new cves entries through NVD API
cves = get_cves(5)

# filter out undesired cves based on mathcing rules
filtered_cves = find_matching_entries_test(cves)

"""with open("filtered_cves.json", "w") as outfile:
    json.dump(filtered_cves, outfile)"""

print("matched cves")
print(filtered_cves)


# test entry for job creation
# entry = """
#        {
#        "id": "CVE-2014-0050",
#        "repository": "https://github.com/apache/commons-fileupload",
#        "version": "1.3:1.3.1"
#        }
#    """

if filtered_cves:
    for entry in filtered_cves:
        create_prospector_job(entry)
