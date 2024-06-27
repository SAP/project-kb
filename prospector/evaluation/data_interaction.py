import json
from datetime import datetime

from data_sources.nvd.filter_entries import (
    find_matching_entries_test,
    get_cve_by_id,
    get_cves,
)


FILEPATH_SINGLE_CVE = "evaluation/single_cve.json"
FILEPATH_MULTIPLE_CVES = "evaluation/multiple_cves.json"


def save_single_cve():
    with open(FILEPATH_SINGLE_CVE, "w") as f:
        data = get_cve_by_id("CVE-2020-1925")
        filtered_cves = find_matching_entries_test(data)
        json.dump(filtered_cves, f)
        print("Saved a single CVEs.")


def save_multiple_cves():
    with open(FILEPATH_MULTIPLE_CVES, "w") as f:
        data = get_cves(10)
        filtered_cves = find_matching_entries_test(data)
        json.dump(filtered_cves, f)
        print("Saved multiple CVEs.")


def load_single_cve():
    with open(FILEPATH_SINGLE_CVE, "r") as f:
        json_data = json.load(f)
        return json_data


def load_multiple_cves():
    with open(FILEPATH_MULTIPLE_CVES, "r") as f:
        return json.load(f)
