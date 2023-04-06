import csv
import json
import requests
import json
import datetime
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
        # print(data["vulnerabilities"])

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


# Given the list of entries in json format filter them and
def find_matching_entries(data):
    # TODO decide the format and strucutre of the match list
    match_list = csv_to_json(
        "/home/matt/sap/project-kb/prospector/data_sources/test.csv"
    )
    match_list = json.loads(match_list)

    filtered_cves = []
    relevant_info_cves = []
    # descriptions = []

    for vuln in data["vulnerabilities"]:
        print(vuln["cve"]["id"])
        # descriptions.append(vuln["cve"]["descriptions"][0]["value"])
        for rule in match_list:
            # TODO improve the matching condition
            if (
                rule["service_name"].lower()
                in vuln["cve"]["descriptions"][0]["value"].lower()
            ):
                # save the whole object containing all info
                filtered_cves.append(vuln)
                # extract only relevant info and save them into a new dict
                relevant_info_cves.append(extract_cve_info(vuln, rule))
        # write_list_to_file(descriptions, "out_descriptions.txt")

    return relevant_info_cves


def write_list_to_file(lst, filename):
    with open(filename, "w") as file:
        for item in lst:
            file.write(str(item) + "\n")


def extract_cve_info(entry, rule):
    cve_id = entry["cve"]["id"]
    desc = entry["cve"]["descriptions"][0]["value"]
    version = "None:None"
    repo = rule["repository"]
    vulnStatus = entry["cve"]["vulnStatus"]

    # TODO: version ranges extracted only from cpe. Need to check also text description
    lst_version_ranges = extract_version_ranges_cpe(entry["cve"])
    version = process_ranges(lst_version_ranges)

    print(version)

    relevant_info_dict = {
        "id": cve_id,
        "description": desc,
        "version": version,
        "repository": repo,
        "vulnStatus": vulnStatus,
    }

    return relevant_info_dict
