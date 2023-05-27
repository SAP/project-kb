import csv
import datetime
import json

import requests
from versions_extraction import extract_version_ranges_cpe, process_ranges


def get_cves(d_time):
    data = ""
    # Set up the URL to retrieve the latest CVE entries from NVD
    nvd_url = "https://services.nvd.nist.gov/rest/json/cves/2.0?"

    # calculate the date to retrieve new entries (%Y-%m-%dT%H:%M:%S.%f%2B01:00)
    date_now = datetime.datetime.now()
    start_date = (date_now - datetime.timedelta(days=d_time)).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    end_date = date_now.strftime("%Y-%m-%dT%H:%M:%S")

    nvd_url += f"lastModStartDate={start_date}&lastModEndDate={end_date}"

    # Retrieve the data from NVD
    try:
        print(nvd_url)
        response = requests.get(nvd_url)
    except Exception as e:
        print(str(e))

    if response.status_code == 200:
        data = json.loads(response.text)

    else:
        print("Error while trying to retrieve entries")

    return data


def get_cve_by_id(id):
    nvd_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveID={id}"

    try:
        print(nvd_url)
        response = requests.get(nvd_url)
    except Exception as e:
        print(str(e))

    if response.status_code == 200:
        data = json.loads(response.text)
        # print(data["vulnerabilities"])

    else:
        print("Error while trying to retrieve entries")

    return data


def write_list_to_file(lst, filename):
    with open(filename, "w") as file:
        for item in lst:
            file.write(str(item) + "\n")


def csv_to_json(csv_file_path):
    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        data = []
        # Skip the header row
        next(csv_reader)
        # Loop through the rows of the file
        for row in csv_reader:
            # Create a dictionary for the row data
            row_data = {"project": row[0], "service_name": row[1], "repository": row[2]}
            data.append(row_data)
    # Convert to JSON object
    json_data = json.dumps(data)
    return json_data


def find_matching_entries_test(data):
    with open("./data/project_metadata.json", "r") as f:
        match_list = json.load(f)

    filtered_cves = []

    for vuln in data["vulnerabilities"]:
        for data in match_list.values():
            keywords = data["search keywords"]
            for keyword in keywords:
                if keyword in vuln["cve"]["descriptions"][0]["value"]:
                    lst_version_ranges = extract_version_ranges_cpe(vuln["cve"])
                    version = process_ranges(lst_version_ranges)
                    filtered_cves.append(
                        {
                            "nvd_info": vuln,
                            "repo_url": data["git"],
                            "version_interval": version,
                        }
                    )
                    print(vuln["cve"]["id"])
                    break

    return filtered_cves
