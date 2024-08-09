from collections import defaultdict
import csv
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

# The number of top commits to consider for 'high confidence' classification
NUM_TOP_COMMITS = 10

cc_rule_as_strong_rule = True
# Whether to use the old rule names (old: COMMIT_IN_REFERENCE,
# CVE_ID_IN_MESSAGE, CVE_ID_IN_LINKED_ISSUE, CROSS_REFERENCED_JIRA_LINK,
# CROSS_REFERENCED_GH_LINK)
use_old_rule_names = True if "matteo" in PROSPECTOR_REPORT_PATH else False


def _choose_strong_rules(
    cc_rule_as_strong_rule: bool, use_old_rule_names: bool
) -> List[str]:
    """Return the list of strong rules, given the settings."""
    if cc_rule_as_strong_rule and not use_old_rule_names:
        STRONG_RULES = [
            "COMMIT_IN_REFERENCE",
            "VULN_ID_IN_MESSAGE",
            "XREF_BUG",
            "XREF_GH",
            "VULN_ID_IN_LINKED_ISSUE",
            "COMMIT_IS_SECURITY_RELEVANT",
        ]
    elif use_old_rule_names and not cc_rule_as_strong_rule:
        STRONG_RULES = [
            "COMMIT_IN_REFERENCE",
            "CVE_ID_IN_MESSAGE",
            "CROSS_REFERENCED_JIRA_LINK",
            "CROSS_REFERENCED_GH_LINK",
            "CVE_ID_IN_LINKED_ISSUE",
        ]
    else:
        STRONG_RULES = [
            "COMMIT_IN_REFERENCE",
            "VULN_ID_IN_MESSAGE",
            "XREF_BUG",
            "XREF_GH",
            "VULN_ID_IN_LINKED_ISSUE",
        ]

    return STRONG_RULES


STRONG_RULES = _choose_strong_rules(cc_rule_as_strong_rule, use_old_rule_names)


if not cc_rule_as_strong_rule and not use_old_rule_names:
    WEAK_RULES = [
        "CHANGES_RELEVANT_FILES",
        "COMMIT_IS_SECURITY_RELEVANT",
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
else:
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
    # dataset = dataset[:100]  # Actual line number in D53.csv -2
    # dataset = dataset[198:199]  # Actual line number in D53.csv -2

    # Keep track of how many reports were attempted to be analysed
    attempted_count = 0
    # Keep track of how many reports were actually analysed
    analysed_reports_count = 0
    # Keep track of the CVEs where there is no report file
    reports_not_found = []

    #### Data to insert into table
    if use_old_rule_names:
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
    else:
        results = {
            "high": [],
            "COMMIT_IN_REFERENCE": [],
            "VULN_ID_IN_MESSAGE": [],
            "VULN_ID_IN_LINKED_ISSUE": [],
            "XREF_BUG": [],
            "XREF_GH": [],
            "COMMIT_IS_SECURITY_RELEVANT": [],
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
    if use_old_rule_names:
        results["CROSS_REFERENCED_JIRA_LINK"] += results[
            "CROSS_REFERENCED_GH_LINK"
        ]
        results.pop("CROSS_REFERENCED_GH_LINK")
    # Remove the cc rule count before writing to the table as the table doesn't include it
    else:
        if cc_rule_as_strong_rule:
            logger.info(
                f"CC Rule matched for {len(results['COMMIT_IS_SECURITY_RELEVANT'])}: {results['COMMIT_IS_SECURITY_RELEVANT']}"
            )
            results.pop("COMMIT_IS_SECURITY_RELEVANT")

        results["XREF_BUG"] += results["XREF_GH"]
        results.pop("XREF_GH")

    logger.info(f"Ran analysis on {PROSPECTOR_REPORT_PATH}.")

    for key, v in results.items():
        if type(v) == list:
            v = len(v)
        logger.info(f"\t{v}\t{key}")
        table_data.append([v, round(v / analysed_reports_count * 100, 2)])

    # Generate the Latex table
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
    path = _save_summary_execution_details(results, reports_not_found)
    logger.info(
        f"Saved summary execution details (lists of CVEs for each category) to {path}."
    )


def _analyse_report(
    results: dict, cve_id: str, report_data, true_fixing_commits: list
):
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

    if len(true_fixing_commits_in_report) == 0:
        # If there are no candidates at all -> not reported
        existing_candidates = report_data["commits"]
        if existing_candidates:
            # check if it's a false positive (it matched a strong rule)
            strong_matched_rules = [
                rule["id"]
                for rule in report_data["commits"][0]["matched_rules"]
                if rule["id"] in STRONG_RULES
            ]
            if strong_matched_rules:
                results["false_positive"].append(cve_id)
                return
        # otherwise, there are no candidates or it's not a false positive
        results["not_reported"].append(cve_id)
        return

    # Fixing commit is among the candidates of the report
    if len(true_fixing_commits_in_report) >= 0:
        for i, commit in enumerate(report_data["commits"]):
            # Get candidates and twins that are fixing commits
            candidate_and_twins = _get_candidate_and_twins_ids(commit)
            candidates_in_fixing_commits = _list_intersection(
                candidate_and_twins, true_fixing_commits
            )

            # First candidate is one of the fixing commits
            if i <= NUM_TOP_COMMITS and candidates_in_fixing_commits:
                matched_rules = [rule["id"] for rule in commit["matched_rules"]]
                strong_matched_rules = list(
                    set(STRONG_RULES).intersection(set(matched_rules))
                )
                # increase count at high, but only count once here
                if len(strong_matched_rules) > 0:
                    results["high"].append(cve_id)

                    for strong_matched_rule in strong_matched_rules:
                        results[strong_matched_rule].append(cve_id)
                    return

                # # check for strong rules
                # for rule in STRONG_RULES:
                # mutually exclusive
                # if rule in matched_rules:
                #     results[rule].append(cve_id)
                #     results["high"].append(cve_id)
                #     return

            if i <= 0 and candidates_in_fixing_commits:
                # check for weak rules
                weak_matched_rules = set(matched_rules).intersection(WEAK_RULES)
                if weak_matched_rules:
                    results["medium"].append(cve_id)
                    return

            # Fixing commit among the first 10 (low confidence)
            if i > 0 and i < 10 and candidates_in_fixing_commits:
                results["low"].append(cve_id)
                return

            # Commit not among the first 10 (not found)
            if i >= 10:
                results["not_found"].append(cve_id)
                return

        logger.info(f"This shouldn't happen {cve_id}")


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


def _save_summary_execution_details(
    results: dict, reports_not_found: list
) -> str:
    """Saves the detailed content (including the list of CVEs for each category
    of the summary execution table to a JSON file.

    Returns:
        The filepath where the details were saved to.
    """
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
    return detailed_results_output_path


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
    """Analyse which CVEs changed category in different executions given two
    JSON files with the detailed summary execution results.

    The detailed summary execution results are created when executing
    `analyse_prospector_reports`. Uses the last entry in these files.

    Saves the output to `summary_execution/flow-analysis.json`.
    """
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


def analyse_category_flows_no_mutual_exclusion():
    """Analyse which CVEs changed category in different executions given two
    JSON files with the detailed summary execution results.

    The detailed summary execution results are created when executing
    `analyse_prospector_reports`. Uses the last entry in these files.

    Saves the output to `summary_execution/flow-analysis.json`.
    """
    data1 = load_json_file(COMPARE_DIRECTORY_1)["summary_execution_details"][-1]
    data2 = load_json_file(COMPARE_DIRECTORY_2)["summary_execution_details"][-1]

    # Skip the `high` category
    categories = [
        "COMMIT_IN_REFERENCE",
        "VULN_ID_IN_MESSAGE",
        "VULN_ID_IN_LINKED_ISSUE",
        "XREF_BUG",
        "medium",
        "low",
        "not_found",
        "not_reported",
        "false_positive",
        "missing",
    ]

    # Create the dictionary structure
    transitions = {}

    for category in categories:
        transitions[category] = {"data1": [], "data2": []}

    # Whichever ones do not have a report in both sets (Matteo and me), do not consider them and just list them as missing.
    transitions["missing"]["data1"] = data1["missing"]
    transitions["missing"]["data2"] = data2["missing"]

    missing = data1["missing"] + data2["missing"]

    categories.remove("missing")
    # For each category, get which ones are in first, but not in second and in second but not in first
    for category in categories:
        d1, d2 = _get_symmetric_difference(
            data1["results"][category], data2["results"][category], missing
        )
        transitions[category]["data1"] = d1
        transitions[category]["data2"] = d2

    save_dict_to_json(
        transitions,
        f"{ANALYSIS_RESULTS_PATH}summary_execution/flow-analysis.json",
    )


def _get_symmetric_difference(list1: list, list2: list, ignore: list):
    """Returns two lists: the first containing elements that are only in list1
    but not in list2 and the second one vice versa.
    """
    return list(set(list1) - set(list2) - set(ignore)), list(
        set(list2) - set(list1) - set(ignore)
    )


def difference_ground_truth_datasets():
    """To find out if two ground truth datasets contain the same CVEs."""
    filepath1 = "evaluation/data/input/d63.csv"
    filepath2 = "evaluation/data/input/d63_mvi.csv"

    dataset1 = load_dataset(filepath1)
    dataset2 = load_dataset(filepath2)

    ids_dataset1 = set(record[0] for record in dataset1)
    ids_dataset2 = set(record[0] for record in dataset2)

    unique_to_file1 = ids_dataset1 - ids_dataset2
    unique_to_file2 = ids_dataset2 - ids_dataset1

    print(f"IDs in {filepath1} but not in {filepath2}:")
    for id in sorted(unique_to_file1):
        print(id)

    print(f"\nIDs in {filepath2} but not in {filepath1}:")
    for id in sorted(unique_to_file2):
        print(id)

    # Find differences in fixing commits
    different_fixing_commits = []

    ids_and_fixing1 = {}
    for record in dataset1:
        ids_and_fixing1[record[0]] = record[4]

    ids_and_fixing2 = {}
    for record in dataset2:
        ids_and_fixing2[record[0]] = record[4]

    for k, v in ids_and_fixing1.items():
        if v != ids_and_fixing2.get(k, ""):
            different_fixing_commits.append((k, v))

    print(f"\nDifferent fixing commits: {len(different_fixing_commits)}")
