import csv
import json
import re
from typing import Dict, List


def load_dataset_file(file_path: str) -> List[Dict]:
    with open(file_path, "r") as f:
        reader = csv.reader(f, delimiter=";")
        return [row for row in reader if bool(re.match(r"CVE-\d{4}-\d{4,8}", row[0]))]


def check_rule_strenght(rules: List[Dict]):
    for rule in rules:
        if rule["id"] == "COMMIT_IN_REFERENCE":
            return 1
        if rule["relevance"] > 30:
            return 2

    return 0


def analyze_report(report_file: str, commits: str):
    with open(report_file, "r") as f:
        report = json.load(f)
        for rank, commit in enumerate(report["commits"]):

            rules_strenght = check_rule_strenght(commit["matched_rules"])

            # If the commit is contained in the ground truth
            if commit["commid_id"] in commits:
                return (
                    True,
                    rules_strenght,
                    commit["commit_id"],
                    rank,
                )
            # If a twin of the commit is contained in the ground truth
            for twin in commit["twins"]:
                if twin[1] in commits:
                    return (
                        True,
                        rules_strenght,
                        commit["commit_id"],
                        rank,
                    )
            # If the commit is not contained in the ground truth but matches a strong rule
            if rules_strenght > 0:
                return (
                    False,
                    rules_strenght,
                    commit["commit_id"],
                    rank,
                )
        return False, 0, "", -1


def analyze_results(dataset_path: str):
    cves = load_dataset_file(dataset_path)
    results = {
        "analyzed": {"found": {}, "not_found": {}},
        "not_analyzed": [],
        "not_sure": [],
    }
    for cve in cves:
        try:
            is_fix, rule_type, commit, rank = analyze_report(
                f"{dataset_path[:-4]}/{cve[0]}.json", cve[4]
            )
        except FileNotFoundError:
            results["not_analyzed"].append(cve[0])
