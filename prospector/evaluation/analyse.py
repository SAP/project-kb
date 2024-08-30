from collections import defaultdict
from datetime import datetime
import json
import os
from typing import List
import plotly.graph_objects as go
from plotly.io import write_image

from tqdm import tqdm

from evaluation.utils import (
    COMPARISON_DIRECTORY,
    load_dataset,
    load_json_file,
    save_dict_to_json,
    update_summary_execution_table,
    logger,
    INPUT_DATA_PATH,
    PROSPECTOR_REPORTS_PATH_HOST,
    ANALYSIS_RESULTS_PATH,
    BATCH,
)

# The number of top commits to consider for 'high confidence' classification
NUM_TOP_COMMITS = 5
# NUM_TOP_COMMITS = 10

if BATCH in ["regular", "old_code"]:
    STRONG_RULES = [
        "COMMIT_IN_REFERENCE",
        "VULN_ID_IN_MESSAGE",
        "XREF_BUG",
        "XREF_GH",
        "VULN_ID_IN_LINKED_ISSUE",
        "COMMIT_IS_SECURITY_RELEVANT",
    ]
else:
    STRONG_RULES = [
        "COMMIT_IN_REFERENCE",
        "CVE_ID_IN_MESSAGE",
        "CROSS_REFERENCED_JIRA_LINK",
        "CROSS_REFERENCED_GH_LINK",
        "CVE_ID_IN_LINKED_ISSUE",
        "COMMIT_IS_SECURITY_RELEVANT",
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


def analyse_prospector_reports(filename: str, selected_cves: str):
    """Analyses Prospector reports. Creates the summary_execution_results table."""
    file = INPUT_DATA_PATH + filename + ".csv"
    dataset = load_dataset(file)
    # dataset = dataset[:100]  # Actual line number in D53.csv -2
    # dataset = dataset[198:199]  # Actual line number in D53.csv -2
    if selected_cves != "all" and len(selected_cves) != 0:
        dataset = [c for c in dataset if c[0] in selected_cves]

    # Keep track of how many reports were attempted to be analysed
    attempted_count = 0
    # Keep track of how many reports were actually analysed
    analysed_reports_count = 0
    # Keep track of the CVEs where there is no report file
    reports_not_found = []

    #### Data to insert into table
    if BATCH in ["regular", "old_code"]:
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
            "aborted": [],
        }
    else:
        results = {
            "high": [],
            "COMMIT_IN_REFERENCE": [],
            "CVE_ID_IN_MESSAGE": [],
            "CVE_ID_IN_LINKED_ISSUE": [],
            "CROSS_REFERENCED_JIRA_LINK": [],
            "CROSS_REFERENCED_GH_LINK": [],
            "COMMIT_IS_SECURITY_RELEVANT": [],
            "medium": [],
            "low": [],
            "not_found": [],
            "not_reported": [],
            "false_positive": [],
            "aborted": [],
        }

    print(f"Analysing reports in {PROSPECTOR_REPORTS_PATH_HOST}")
    logger.info(f"Attempting to analyse {len(dataset)} CVEs.")

    for record in tqdm(dataset, total=len(dataset), desc="Analysing Records"):
        # ID;URL;VERSIONS;FLAG;COMMITS;COMMENTS
        cve_id = record[0]
        true_fixing_commits = record[4].split(",")

        attempted_count += 1

        try:
            with open(f"{PROSPECTOR_REPORTS_PATH_HOST}/{cve_id}.json") as file:
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

        except Exception as e:
            logger.info(f"Error occured for {cve_id}: {e}")
            continue
    # Append aborted reports to results object
    results["aborted"] = reports_not_found

    if BATCH == "regular":
        update_summary_execution_table(
            results=results,
            total=analysed_reports_count,
        )

    logger.info(f"Ran analysis on {PROSPECTOR_REPORTS_PATH_HOST}.")
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

            if i <= NUM_TOP_COMMITS and candidates_in_fixing_commits:
                # if i <= 0 and candidates_in_fixing_commits:
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
    batch_name = os.path.basename(
        os.path.normpath(PROSPECTOR_REPORTS_PATH_HOST)
    )
    detailed_results_output_path = (
        f"{ANALYSIS_RESULTS_PATH}summary_execution_{batch_name}.json"
    )
    printout = {
        "timestamp": datetime.now().strftime("%d-%m-%Y, %H:%M"),
        "results": results,
        # "missing": reports_not_found,
    }
    printout["results"]["missing"] = reports_not_found
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
    generated_reports = []

    print(f"Counting reports in {PROSPECTOR_REPORTS_PATH_HOST}")

    for record in dataset:
        cve_id = record[0]

        if os.path.isfile(f"{PROSPECTOR_REPORTS_PATH_HOST}/{cve_id}.json"):
            generated_reports.append(cve_id)
        else:
            missing_reports.append(cve_id)

    print(
        f"There are {len(dataset) - len(missing_reports)} reports. Reports are missing for {len(missing_reports)} CVEs: {missing_reports}"
    )

    # print(*generated_reports, sep=",")


def analyse_category_flows():
    """Analyse which CVEs changed category in different executions given two
    JSON files with the detailed summary execution results.

    The detailed summary execution results are created when executing
    `analyse_prospector_reports`. Uses the last entry in these files.

    Saves the output to `summary_execution/flow-analysis.json`.
    """
    summary_execution_file = (
        ANALYSIS_RESULTS_PATH
        + "summary_execution/"
        + PROSPECTOR_REPORTS_PATH_HOST.split("/")[-2]
        + ".json"
    )
    summary_execution_comparison_file = (
        ANALYSIS_RESULTS_PATH
        + "summary_execution/"
        + COMPARISON_DIRECTORY.split("/")[-2]
        + ".json"
    )

    data1 = load_json_file(summary_execution_file)
    data2 = load_json_file(summary_execution_comparison_file)
    print(
        f"Comparing {PROSPECTOR_REPORTS_PATH_HOST} with {COMPARISON_DIRECTORY}"
    )

    # Get the results from both files
    results1 = data1["summary_execution_details"][0]["results"]
    results2 = data2["summary_execution_details"][0]["results"]

    transitions, adjustments = _process_cve_transitions(results1, results2)

    # Create the final output structure
    output_data = {
        "transitions": [{k: v} for k, v in transitions.items()],
        "category_adjustments": {k: v for k, v in adjustments.items()},
    }

    save_dict_to_json(
        output_data,
        f"{ANALYSIS_RESULTS_PATH}summary_execution/flow-analysis.json",
    )


def _process_cve_transitions(results1, results2):
    transitions = defaultdict(list)
    adjustments = defaultdict(int)
    categories = [
        "high",
        "medium",
        "low",
        "not_found",
        "not_reported",
        "false_positive",
        # "missing",
    ]

    for cat1 in categories:
        for cat2 in categories:
            if cat1 == cat2:
                continue

            cves_moving = set(results1[cat1]) & set(results2[cat2])
            for cve in cves_moving:
                if cat1 != "missing" and cat2 != "missing":
                    report1 = load_json_file(
                        f"{PROSPECTOR_REPORTS_PATH_HOST}/{cve}.json"
                    )
                    report2 = load_json_file(
                        f"{COMPARISON_DIRECTORY}/{cve}.json"
                    )
                    # is the first commit different?
                    if (
                        len(report1["commits"]) > 0
                        and len(report2["commits"]) > 0
                    ):
                        first_commit_same = (
                            report1["commits"][0]["commit_id"]
                            == report2["commits"][0]["commit_id"]
                        )
                        cve_info = {
                            "different first commit": not first_commit_same
                        }
                    else:
                        cve_info = {"different first commit": False}

                    different_refs = _compare_references(
                        report1["advisory_record"]["references"],
                        report2["advisory_record"]["references"],
                    )

                    # cve_info = {"different references": different_refs}
                    cve_info["different references"] = different_refs

                    # If references are the same, check commits
                    if not different_refs:
                        different_keywords = _compare_keywords(
                            report1["advisory_record"]["keywords"],
                            report2["advisory_record"]["keywords"],
                        )

                        cve_info["different keywords"] = different_keywords

                        if not different_keywords:
                            commits1 = [
                                commit["commit_id"]
                                for commit in report1["commits"]
                            ]
                            commits2 = [
                                commit["commit_id"]
                                for commit in report2["commits"]
                            ]
                            same_commits_diff_order = _compare_commits(
                                commits1, commits2
                            )
                            cve_info["same commits, ordered differently"] = (
                                same_commits_diff_order
                            )

                            if not same_commits_diff_order:
                                relevance_sum1 = _sum_relevance(
                                    report1["commits"]
                                )
                                relevance_sum2 = _sum_relevance(
                                    report2["commits"]
                                )
                                cve_info["same relevance sum"] = (
                                    relevance_sum1 == relevance_sum2
                                )

                transitions[f"{cat1} to {cat2}"].append({cve: cve_info})
                adjustments[cat1] -= 1
                adjustments[cat2] += 1

    return transitions, adjustments


def _sum_relevance(commits):
    # Calculate the sum of relevance for rules in the first 10 commits
    relevance_sum = 0
    for commit in commits[:10]:
        relevance_sum += sum(
            rule["relevance"] for rule in commit["matched_rules"]
        )
    return relevance_sum


def _compare_references(refs1, refs2):
    return refs1 != refs2


def _compare_keywords(keyws1, keyws2):
    return set(keyws1) != set(keyws2)


def _compare_commits(commits1, commits2):
    # Check if the two lists of commits contain the same elements, but possibly in different order
    return sorted(commits1) == sorted(commits2) and commits1 != commits2


def generate_checkmarks_table(input_dataset: str, selected_cves):
    """
    Generates a table containing matched rules for each fixing commit in the generated reports. The table also contains the total overall execution time and the total LLM execution time.

    Args:
        json_folder (str): The path to the folder containing the JSON reports.
        output_file (str): The path to the output LaTeX file.

    Returns:
        None
    """
    # Define the list of all rules
    all_rules = [
        "VULN_ID_IN_MESSAGE",
        "XREF_BUG",
        "XREF_GH",
        "COMMIT_IN_REFERENCE",
        "COMMIT_IS_SECURITY_RELEVANT",
        "VULN_ID_IN_LINKED_ISSUE",
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

    # Start the LaTeX table
    latex_column_titles = [rule.replace("_", "\\_") for rule in all_rules]
    latex_content = (
        """\\begin{longtabu} to \\textwidth { c | """
        + " | ".join(["c" for _ in all_rules])
        + """ | c | c }
\\caption{Matched rules for each fixing commit}\\\\
    \\toprule
    & """
        + " & ".join([f"\\rot{{{rule}}}" for rule in latex_column_titles])
        + """ & \\rot{Total Execution Time} & \\rot{LLM Execution Time} \\\\ \\midrule
    """
    )

    # Go through every CVE-ID + fixing commit pair in the input dataset:
    file = INPUT_DATA_PATH + input_dataset + ".csv"
    dataset = load_dataset(file)

    if len(selected_cves) != 0:
        dataset = [c for c in dataset if c[0] in selected_cves]

    for record in tqdm(dataset, total=len(dataset), desc="Analysing Records"):
        cve_id = record[0]
        fixing_commits = record[4].split(",")

        # Open the report file, and get
        # - the fixing candidate's matched rules
        # - the overall execution time
        # - the sum of the LLM execution times
        try:
            with open(f"{PROSPECTOR_REPORTS_PATH_HOST}/{cve_id}.json") as file:
                report = json.load(file)

        except FileNotFoundError:
            logger.debug(f"Couldn't find report for {cve_id}")
            continue

        except Exception as e:
            logger.info(f"Error occured for {cve_id}: {e}")
            continue

        matched_rules = []
        # filter commits and calculate their total relevance
        relevant_commits = [
            {
                "commit_id": commit["commit_id"],
                "total_relevance": _calculate_total_relevance(commit),
                "matched_rules": commit["matched_rules"],
            }
            for commit in report["commits"]
            if commit["commit_id"] in fixing_commits
        ]

        if relevant_commits:
            fixing_candidate = max(
                relevant_commits, key=lambda x: x["total_relevance"]
            )

            matched_rules = [
                rule["id"] for rule in fixing_candidate.get("matched_rules")
            ]

        else:
            # Don't save?
            print(f"Did not add {cve_id}.json to the table.")
            continue

        overall_exectime = round(
            report["processing_statistics"]["core"]["execution time"][0], 2
        )
        llm_exectime = round(
            sum(
                report["processing_statistics"]["LLM"]["commit_classification"][
                    "execution time"
                ]
            ),
            2,
        )

        # Initialise a row with the CVE ID
        row = [cve_id]

        rule_checks = {rule: "" for rule in all_rules}
        for r in matched_rules:
            rule_checks[r] = "\checkmark"

        row.extend([rule_checks[r] for r in all_rules])
        row.extend([str(overall_exectime), str(llm_exectime)])

        # Add the row to the latex content
        latex_content += " & ".join(row) + "\\\\ \\midrule \n"

    # End latex table
    latex_content += "\\bottomrule\n\\end{longtabu}"

    # Write the content to the output file
    with open(
        ANALYSIS_RESULTS_PATH + "summary_execution/checkmarks_table.tex", "w"
    ) as file:
        file.writelines(latex_content)


def _calculate_total_relevance(commit):
    return sum(rule["relevance"] for rule in commit["matched_rules"])


def generate_sankey_diagram(file1: str, file2: str, file3: str):
    # Load JSON data
    summary_execution_file_1 = (
        ANALYSIS_RESULTS_PATH + "summary_execution/" + file1 + ".json"
    )
    summary_execution_file_2 = (
        ANALYSIS_RESULTS_PATH + "summary_execution/" + file2 + ".json"
    )
    summary_execution_file_3 = (
        ANALYSIS_RESULTS_PATH + "summary_execution/" + file3 + ".json"
    )

    summary1 = load_json_file(summary_execution_file_1)
    summary2 = load_json_file(summary_execution_file_2)
    summary3 = load_json_file(summary_execution_file_3)

    print(
        f"Comparing {summary_execution_file_1}, {summary_execution_file_2}, and {summary_execution_file_3}"
    )

    # Ignore sub categories of "high"
    categories_to_include = [
        "high",
        "medium",
        "low",
        "not_found",
        "not_reported",
        "false_positive",
        "aborted",
        "missing",
    ]
    # Extract results from both files
    results1 = summary1["summary_execution_details"][-1]["results"]
    results2 = summary2["summary_execution_details"][-1]["results"]
    results3 = summary3["summary_execution_details"][-1]["results"]

    # Filter results to include only specified categories
    results1 = {k: v for k, v in results1.items() if k in categories_to_include}
    results2 = {k: v for k, v in results2.items() if k in categories_to_include}
    results3 = {k: v for k, v in results3.items() if k in categories_to_include}

    # Create a mapping of CVEs to their categories for both files
    cve_categories1 = {
        cve: category for category, cves in results1.items() for cve in cves
    }
    cve_categories2 = {
        cve: category for category, cves in results2.items() for cve in cves
    }
    cve_categories3 = {
        cve: category for category, cves in results3.items() for cve in cves
    }

    # Get all unique CVEs and categories
    all_cves = set(cve_categories1.keys())

    # Create node labels
    node_labels = categories_to_include * 3

    # Create source, target, and value lists for Sankey diagram
    source = []
    target = []
    value = []
    link_colours = []

    # Count movements between categories
    movements12 = defaultdict(int)
    movements23 = defaultdict(int)
    for cve in all_cves:
        cat1 = cve_categories1.get(cve, None)
        cat2 = cve_categories2.get(cve, None)
        cat3 = cve_categories3.get(cve, None)
        if not cat1 or not cat2 or not cat3:
            print(f"No category for {cve}")
            continue
        movements12[(cat1, cat2)] += 1
        movements23[(cat2, cat3)] += 1

    # Assign colors to categories
    category_colors = {
        "high": "steelblue",
        "medium": "dodgerblue",
        "low": "cornflowerblue",
        "not_found": "teal",
        "not_reported": "cadetblue",
        "false_positive": "lightgreen",
        "aborted": "palegreen",
        "missing": "gray",
    }

    # Create node colors
    node_colors = [category_colors[cat] for cat in categories_to_include] * 3

    # Convert movements to source, target, and value lists
    category_to_index = {cat: i for i, cat in enumerate(categories_to_include)}

    # First half, movements from file1 to file2
    for (cat1, cat2), count in movements12.items():
        source.append(category_to_index[cat1])
        target.append(category_to_index[cat2] + len(categories_to_include))
        value.append(count)
        if cat1 == cat2:
            link_colours.append("lightgray")
        else:
            link_colours.append(category_colors[cat1])

    # Second half: Movements from file2 to file3
    for (cat2, cat3), count in movements23.items():
        source.append(category_to_index[cat2] + len(categories_to_include))
        target.append(category_to_index[cat3] + 2 * len(categories_to_include))
        value.append(count)
        if cat2 == cat3:
            link_colours.append("lightgray")
        else:
            link_colours.append(category_colors[cat2])

    # Create the Sankey diagram
    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=node_labels,
                    color=node_colors,
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=value,
                    color=link_colours,
                ),
            )
        ]
    )

    fig.update_layout(
        title_text=f"CVE Category Changes between {file1}, {file2}, and {file3}",
        font_size=14,
        width=1200,
        height=800,
    )

    output_file = (
        ANALYSIS_RESULTS_PATH + "plots/" + f"sankey-{file1}-{file2}-{file3}.png"
    )
    # Save as PNG
    write_image(fig, output_file)
    print(f"Sankey diagram saved to {output_file}")
