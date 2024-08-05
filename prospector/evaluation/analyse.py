from collections import defaultdict
from datetime import datetime
import json
import os
from typing import List

from tqdm import tqdm

from evaluation.utils import (
    COMPARE_DIRECTORY_1,
    COMPARE_DIRECTORY_2,
    load_dataset,
    load_json_file,
    save_dict_to_json,
    update_summary_execution_table,
    logger,
    INPUT_DATA_PATH,
    PROSPECTOR_REPORT_PATH,
    ANALYSIS_RESULTS_PATH,
)


# STRONG_RULES = [
#     "COMMIT_IN_REFERENCE",
#     "VULN_ID_IN_MESSAGE",
#     "XREF_BUG",
#     "XREF_GH",
#     "VULN_ID_IN_LINKED_ISSUE",
# ]
# Analyse old reports before rule names changed
STRONG_RULES = [
    "COMMIT_IN_REFERENCE",
    "CVE_ID_IN_MESSAGE",
    "CROSS_REFERENCED_JIRA_LINK",
    "CROSS_REFERENCED_GH_LINK",
    "CVE_ID_IN_LINKED_ISSUE",
]

WEAK_RULES = [
    "CHANGES_RELEVANT_FILES",
    "CHANGES_RELEVANT_CODE",
    "RELEVANT_WORDS_IN_MESSAGE",
    "ADV_KEYWORDS_IN_FILES",
    "ADV_KEYWORDS_IN_MSG",
    "SEC_KEYWORDS_IN_MESSAGE",
    "SEC_KEYWORDS_IN_LINKED_GH",
    "SEC_KEYWORDS_IN_LINKED_BUG",
    "GITHUB_ISSUE_IN_MESSAGE",
    "BUG_IN_MESSAGE",
    "COMMIT_HAS_TWINS",
]


def analyse_prospector_reports(filename: str):
    """Analyses Prospector reports. Creates the summary_execution_results table."""
    file = INPUT_DATA_PATH + filename + ".csv"
    dataset = load_dataset(file)
    # dataset = dataset[746:747]  # Actual line number in D53.csv -2

    # Keep track of how many reports were attempted to be analysed
    attempted_count = 0
    # Keep track of how many reports were actually analysed
    analysed_reports_count = 0
    # Keep track of the CVEs where there is no report file
    reports_not_found = []

    #### Data to insert into table
    results = {
        "high": [],
        "COMMIT_IN_REFERENCE": [],
        "VULN_ID_IN_MESSAGE": [],
        "VULN_ID_IN_LINKED_ISSUE": [],
        "XREF_BUG": [],
        "XREF_GH": [],
        "medium": [],
        "low": [],
        "not_found": [],
        "not_reported": [],
        "false_positive": [],
    }
    # Analyse old reports before rule names changed
    results = {
        "high": [],
        "COMMIT_IN_REFERENCE": [],
        "CVE_ID_IN_MESSAGE": [],
        "CVE_ID_IN_LINKED_ISSUE": [],
        "CROSS_REFERENCED_JIRA_LINK": [],
        "CROSS_REFERENCED_GH_LINK": [],
        "medium": [],
        "low": [],
        "not_found": [],
        "not_reported": [],
        "false_positive": [],
    }

    print(f"Analysing reports in {PROSPECTOR_REPORT_PATH}")
    logger.info(f"Attempting to analyse {len(dataset)} CVEs.")

    for record in tqdm(dataset, total=len(dataset), desc="Analysing Records"):
        # ID;URL;VERSIONS;FLAG;COMMITS;COMMENTS
        cve_id = record[0]
        true_fixing_commits = record[4].split(",")

        attempted_count += 1

        try:
            with open(f"{PROSPECTOR_REPORT_PATH}/{cve_id}.json") as file:
                # Get all commit IDs present in the report
                report_data = json.load(file)

                _analyse_report(
                    results=results,
                    cve_id=cve_id,
                    report_data=report_data,
                    true_fixing_commits=true_fixing_commits,
                )

                analysed_reports_count += 1

        except FileNotFoundError:
            reports_not_found.append(cve_id)
            logger.debug(f"Couldn't find report for {cve_id}")
            continue

    #### Table Data (write to table)
    table_data = []

    # Combine the two Cross Reference rules into one count
    # results["XREF_BUG"] += results["XREF_GH"]
    # results.pop("XREF_GH")
    # Analyse old reports before rule names changed
    results["CROSS_REFERENCED_JIRA_LINK"] += results["CROSS_REFERENCED_GH_LINK"]
    results.pop("CROSS_REFERENCED_GH_LINK")

    logger.info(f"Ran analysis on {PROSPECTOR_REPORT_PATH}.")

    for key, v in results.items():
        if type(v) == list:
            v = len(v)
        logger.info(f"\t{v}\t{key}")
        table_data.append([v, round(v / analysed_reports_count * 100, 2)])

    update_summary_execution_table(
        mode="MVI",
        data=table_data,
        total=str(analysed_reports_count),
        filepath=f"{ANALYSIS_RESULTS_PATH}summary_execution/table.tex",
    )

    logger.info(
        f"Analysed {analysed_reports_count}, couldn't find reports for {len(reports_not_found)} out of {attempted_count} analysis attempts."
    )

    # Save detailed results in a json file (instead of cluttering logs)
    batch_name = os.path.basename(os.path.normpath(PROSPECTOR_REPORT_PATH))
    detailed_results_output_path = (
        f"{ANALYSIS_RESULTS_PATH}summary_execution/{batch_name}.json"
    )
    printout = {
        "timestamp": datetime.now().strftime("%d-%m-%Y, %H:%M"),
        "results": results,
        "missing": reports_not_found,
    }
    try:
        with open(detailed_results_output_path, "r") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {"summary_execution_details": []}

    existing_data["summary_execution_details"].append(printout)

    save_dict_to_json(existing_data, detailed_results_output_path)


def _analyse_report(
    results: dict, cve_id: str, report_data, true_fixing_commits: list
) -> dict:
    """Analyzes a single Prospector report for a given CVE and updates the
    results dictionary.

    Params:
        results (dict): The current results dictionary to be updated.
        cve_id (str): The CVE identifier for the current report.
        report_data (dict): The data from the current Prospector report.
        true_fixing_commits (list): A list of known true fixing commit hashes

    Returns:
        dict: The updated results dictionary.
    """
    true_fixing_commits_in_report = _get_true_fixing_commits_in_report(
        report_data=report_data,
        fixing_commits=true_fixing_commits,
    )

    # Fixing commit is not among the candidates of the report
    if len(true_fixing_commits_in_report) == 0:
        # check if there are any candidates at all
        ranked_candidates = report_data["commits"]
        if not ranked_candidates:
            logger.info(f"Report for {cve_id} does not contain any commits.")
        # else the report does not contain the fixing commit at all
        else:
            logger.debug(
                f"Report for {cve_id} does not contain fixing commit at all."
            )
            # Check if it's a false positive
            strong_matched_rules = [
                rule["id"]
                for rule in report_data["commits"][0]["matched_rules"]
                if rule["id"] in STRONG_RULES
            ]
            if strong_matched_rules:
                results["false_positive"].append(cve_id)
                return results

        results["not_reported"].append(cve_id)
        return results

    #### Find the confidence & count strong rules
    for i, commit in enumerate(report_data["commits"]):
        # Get candidate id and also twins ids
        candidate_and_twins = _get_candidate_and_twins_ids(commit)
        candidates_in_fixing_commits = _list_intersection(
            candidate_and_twins, true_fixing_commits
        )

        # First candidate is one of the fixing commits
        if i == 0 and candidates_in_fixing_commits:
            matched_rules = {rule["id"] for rule in commit["matched_rules"]}

            # check for strong rules
            for rule in STRONG_RULES:
                if rule in matched_rules:
                    results[rule].append(cve_id)
                    results["high"].append(cve_id)
                    return results

            # check for weak rules
            weak_matched_rules = matched_rules.intersection(WEAK_RULES)
            if weak_matched_rules:
                results["medium"].append(cve_id)
                return results

        # Fixing commit among the first 10 (low confidence)
        if i > 0 and i < 10 and candidates_in_fixing_commits:
            results["low"].append(cve_id)
            return results

        # Commit not among the first 10 (not found)
        if i >= 10:
            results["not_found"].append(cve_id)
            return results


def _get_true_fixing_commits_in_report(
    report_data,
    fixing_commits: List[str],
):
    """Return the list of true fixing commits mentioned in the Prospector
    report. Also takes twins into consideration.
    """
    ranked_candidates = []
    for commit in report_data["commits"]:
        ranked_candidates.append(commit["commit_id"])
        if "twins" in commit:
            ranked_candidates.extend([twin[1] for twin in commit["twins"]])

    true_fixing_commits_in_report = [
        commit for commit in ranked_candidates if commit in fixing_commits
    ]

    return true_fixing_commits_in_report


def _get_candidate_and_twins_ids(commit):
    """Combines the candidate's and its twins (if present) IDs into one list
    and returns it."""
    ids = [commit["commit_id"]]
    if "twins" in commit:
        ids.extend([twin[1] for twin in commit["twins"]])

    return ids


def _list_intersection(list1, list2):
    """Returns the common elements of two lists."""
    return list(set(list1) & set(list2))


def count_existing_reports(data_filepath):
    """Prints which CVEs reports are missing for to the console."""
    file = INPUT_DATA_PATH + data_filepath + ".csv"
    dataset = load_dataset(file)

    missing_reports = []

    print(f"Counting reports in {PROSPECTOR_REPORT_PATH}")

    for record in dataset:
        cve_id = record[0]

        if os.path.isfile(f"{PROSPECTOR_REPORT_PATH}/{cve_id}.json"):
            continue
        else:
            missing_reports.append(cve_id)

    print(
        f"There are {len(dataset) - len(missing_reports)} reports. Reports are missing for {len(missing_reports)} CVEs: {missing_reports}"
    )


def analyse_category_flows():
    """Analyse which CVEs changed category in different executions."""
    data1 = load_json_file(COMPARE_DIRECTORY_1)
    data2 = load_json_file(COMPARE_DIRECTORY_2)

    transitions = defaultdict(lambda: defaultdict(list))

    results1 = _create_cve_to_category_mapping(
        data1["summary_execution_details"][-1]["results"]
    )
    results2 = _create_cve_to_category_mapping(
        data2["summary_execution_details"][-1]["results"]
    )

    for cve, category in results1.items():
        new_category = results2.get(cve, None)
        if not new_category:
            print(f"No report for {cve} in second batch.")
            continue

        if results2.get(cve, "") != category:
            transitions[category][new_category].append(cve)

    save_dict_to_json(
        transitions,
        f"{ANALYSIS_RESULTS_PATH}summary_execution/flow-analysis.json",
    )

    # Create a sankey diagram
    # source = transitions.keys()
    # _create_sankey_diagram(source, target, value)


def _create_cve_to_category_mapping(results: dict) -> dict:
    res = {}
    for category in results.keys():
        for cve in results[category]:
            res[cve] = category

    return res


# Create Sankey Diagram to see how the reports change category
def _create_sankey_diagram(source: list, target: list, value: list):
    """Creates a sankey diagram between two files containing summary execution
    details, ie. a json file with a `results` field containing:
        - high
        - commit in reference
        - vuln id in message
        - vuln id in linked issue
        - xref bug
        - medium
        - low
        - not_found
        - not_reported
        - false_positive

    Attention: Not finished!
    """
    data = load_json_file(
        f"{ANALYSIS_RESULTS_PATH}summary_execution/{filename1}.json"
    )
    details = data.get("summary_execution_details", [])
    results = details[-1].get("results", {})

    # Initialize a dictionary to hold transitions
    transitions = defaultdict(lambda: defaultdict(int))

    # Create a list of categories and CVEs
    cve_categories = [
        (category, cve) for category, cves in results.items() for cve in cves
    ]
    for i, (cat1, cve1) in enumerate(cve_categories):
        for cat2, cve2 in cve_categories[i + 1 :]:
            if cve1 == cve2:
                transitions[cat1][cat2] += 1
    print(transitions)
