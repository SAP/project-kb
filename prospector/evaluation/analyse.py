from datetime import datetime
import json
import os
from typing import Dict, List, Tuple

from tqdm import tqdm

from evaluation.utils import (
    load_dataset,
    update_summary_execution_table,
    logger,
    INPUT_DATA_PATH,
    PROSPECTOR_REPORT_PATH,
    ANALYSIS_RESULTS_PATH,
)


STRONG_RULES = [
    "COMMIT_IN_REFERENCE",
    "VULN_ID_IN_MESSAGE",
    "XREF_BUG",
    "XREF_GH",
    "VULN_ID_IN_LINKED_ISSUE",
]
# Analyse old reports before rule names changed
# STRONG_RULES = [
#     "COMMIT_IN_REFERENCE",
#     "CVE_ID_IN_MESSAGE",
#     "CROSS_REFERENCED_JIRA_LINK",
#     "CROSS_REFERENCED_GH_LINK",
#     "CVE_ID_IN_LINKED_ISSUE",
# ]

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
    # results = {
    #     "high": [],
    #     "COMMIT_IN_REFERENCE": [],
    #     "CVE_ID_IN_MESSAGE": [],
    #     "CVE_ID_IN_LINKED_ISSUE": [],
    #     "CROSS_REFERENCED_JIRA_LINK": [],
    #     "CROSS_REFERENCED_GH_LINK": [],
    #     "medium": [],
    #     "low": [],
    #     "not_found": [],
    #     "not_reported": [],
    #     "false_positive": [],
    # }

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
    results["XREF_BUG"] += results["XREF_GH"]
    results.pop("XREF_GH")
    # Analyse old reports before rule names changed
    # results["CROSS_REFERENCED_JIRA_LINK"] += results["CROSS_REFERENCED_GH_LINK"]
    # results.pop("CROSS_REFERENCED_GH_LINK")

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
        filepath=f"{ANALYSIS_RESULTS_PATH}summary_execution_results.tex",
    )

    logger.info(
        f"Analysed {analysed_reports_count}, couldn't find reports for {len(reports_not_found)} out of {attempted_count} analysis attempts."
    )
    logger.debug(f"Strong rules matching: {results['high']}")
    logger.debug(
        f"CVEs matching Commit in reference: {[item[0] for item in results['high'] if item[1] == 'COMMIT_IN_REFERENCE']}"
    )
    logger.debug(f"Weak rules matching: {results['medium']}")

    logger.debug(f"False positive reports: {results['false_positive']}")
    logger.debug(f"Not found reports: {results['not_found']}")


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


def analyse_statistics(filename: str):  # noqa: C901
    """Analyses the Statistics field in each Prospector report of the CVEs contained in `filename`.

    Args:
        filename (str): The input CSV file containing CVE information with the following columns:
        # ID;URL;VERSIONS;FLAG;COMMITS;COMMENTS
        This file must be present in the INPUT_DATA_PATH folder.

    Prints:
        The average time taken for getting the repository URL, for applying the commit classification
        one single time and for applying the commit classification for all X commits.
    """
    file = INPUT_DATA_PATH + filename + ".csv"
    dataset = load_dataset(file)

    missing, files_with_no_commits = [], []
    skipped = 0

    repo_times, cc_times, total_cc_times = [], [], []

    # For each CSV in the input dataset, check its report
    for itm in dataset:
        # Each itm has ID;URL;VERSIONS;FLAG;COMMITS;COMMENTS
        filepath = PROSPECTOR_REPORT_PATH + filename + f"/{itm[0]}.json"
        try:
            repo_time, avg_cc_time, total_cc_time = process_llm_statistics(
                filepath
            )

            repo_times.append(repo_time)
            cc_times.append(avg_cc_time)
            total_cc_times.append(total_cc_time)

        except FileNotFoundError:
            # print(f"Skipped {itm[0]}.json because file could not be found.") # Sanity Check
            missing.append(itm[0])
            skipped += 1

        except ValueError:
            print(f"Skipped {itm[0]}.json.")
            files_with_no_commits.append(itm[0])
            skipped += 1

        finally:
            continue

    avg_repo_time = sum(repo_times) / len(repo_times)
    avg_cc_time = sum(cc_times) / len(cc_times)
    avg_total_cc_time = sum(total_cc_times) / len(total_cc_times)

    # How many commits was the commit classification rule applied to?
    for itm in dataset:
        filepath = PROSPECTOR_REPORT_PATH + filename + f"/{itm[0]}.json"
        try:
            cc_num_commits = get_cc_num_commits(filepath)
            break

        except FileNotFoundError:
            continue

    execution_data = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "total_files_found": len(repo_times),
        "missing_reports": len(missing),
        "skipped_reports": skipped,
        "timings": {
            "avg_time_repo_url": avg_repo_time,
            "avg_time_commit_classification_single": avg_cc_time,
            "avg_time_commit_classification_all": avg_total_cc_time,
        },
    }

    # Load existing data or create new structure
    try:
        with open(ANALYSIS_RESULTS_PATH + "llm_stats.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"executions": []}

    # Add the new execution data
    data["executions"].append(execution_data)

    # Save the updated data
    with open(ANALYSIS_RESULTS_PATH + "llm_stats.json", "w") as f:
        json.dump(data, f, indent=2)


def process_llm_statistics(filepath: str) -> Tuple[float, float, float]:
    """Extracts the LLM statistics saved in Prospector's JSON report.

    Params:
        filepath (str): The filepath to the Prospector report in JSON format.

    Returns:
        Tuple[float, float, float]: (time for getting repository URL, avg.
        time for one commit classification, sum of all commit classification times)
    """
    with open(filepath, "r") as file:
        data = json.load(file)

        try:
            llm_stats = data["processing_statistics"]["LLM"]

            total_cc_time = sum(
                llm_stats["commit_classification"]["execution time"]
            )

            avg_cc_time = total_cc_time / len(
                llm_stats["commit_classification"]["execution time"]
            )

            return (
                llm_stats["repository_url"]["execution time"][0],
                avg_cc_time,
                total_cc_time,
            )

        except Exception as e:
            print(f"Did not have expected JSON fields: {filepath}: {e}")
            raise ValueError


def get_cc_num_commits(filepath):
    """Returns how many commits the commit classification rule was applied to."""
    with open(filepath, "r") as file:
        data = json.load(file)

        num = len(
            data["processing_statistics"]["LLM"]["commit_classification"][
                "execution time"
            ]
        )

        return num


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
        f"There is no report for {len(missing_reports)} CVEs: {missing_reports}"
    )
