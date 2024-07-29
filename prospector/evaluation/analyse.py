import csv
from datetime import datetime
import json
from collections import defaultdict
from typing import Dict, List, Tuple

import seaborn as sns
from matplotlib import pyplot as plt
from tqdm import tqdm

from evaluation.utils import (
    load_dataset,
    update_false_positives,
    update_summary_execution_table,
    logger,
    INPUT_DATA_PATH,
    PROSPECTOR_REPORT_PATH,
    ANALYSIS_RESULTS_PATH,
)


STRONG_RULES = [
    "COMMIT_IN_REFERENCE",
    "VULN_ID_IN_MESSAGE",
    "VULN_ID_IN_LINKED_ISSUE",
    # "XREF_BUG", # LASCHA: fix this, these two XREF ones should be combined
    "XREF_GH",
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


def analyze_results_rules(dataset_path: str):
    """This function analyses Prospector's rule application. It calculates the
    frequency of each rule being matched across the dataset in `dataset_path`.

    It also generates a bar plot visualising the ferquency of each rule being
    matched.

    Prints:
        Precision of the rules table (D6.3 AssureMOSS)
    """
    print(f"Retrieving data from: {dataset_path}")
    dataset = load_dataset(INPUT_DATA_PATH + dataset_path + ".csv")

    rules, table = {}, {}
    count = 0

    for itm in dataset:
        try:
            r, i, v, id = check_report_get_rules(
                PROSPECTOR_REPORT_PATH + dataset_path + "/", itm[0], itm[4]
            )
            if r is not None:
                count += 1
                table[itm[0]] = [id, v, r, itm]
                for rule in r:
                    if rule not in rules:
                        rules[rule] = 1
                    rules[rule] += 1
        except FileNotFoundError:
            continue

    ordered = dict(sorted(rules.items()))
    for k, v in ordered.items():
        print(f"{k} & {v} & {(v / count)*100:.2f}\\% \\\\")

    plt.rcParams["figure.autolayout"] = True
    sns.set_style("whitegrid")
    colors = [
        (
            "#0063B2FF"
            if id
            in (
                "COMMIT_IN_REFERENCE",
                "CROSS_REFERENCED_GH_LINK",
                "CVE_ID_IN_LINKED_ISSUE",
                "CVE_ID_IN_MESSAGE",
            )
            else "#9CC3D5FF"
        )
        for id in ordered.keys()
    ]
    ss = sns.barplot(
        y=list(ordered.keys()),
        x=list(ordered.values()),
        palette=colors,
    )
    ss.set_xscale("log", base=2)
    ss.set_xticks([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
    ss.set_xticklabels([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])

    # ss.set_xticks(range(0, 800, 100))
    ss.tick_params(axis="y", labelsize=8)
    plt.show()
    print(count)
    for k, v in table.items():
        if "CVE_ID_IN_LINKED_ISSUE" in v[2]:
            print(
                f"{v[3][0]};{v[3][1]};{v[3][2]};{v[3][3]};{v[3][4]};{v[3][5]}"
            )
            # print(f"{k}: {v[3]}/commit/{v[0]}")


def analyse_prospector_reports(filename: str):
    """Analyses Prospector reports. Creates the summary_execution_results table."""
    file = INPUT_DATA_PATH + filename + ".csv"
    dataset = load_dataset(file)
    # dataset = dataset[10:15]

    fixing_commit_found = 0
    fixing_commit_not_among_10 = 0
    fixing_commit_not_found = 0

    # Confidence
    confidence = {
        "high": [],
        "medium": [],
        "low": [],
    }

    strong_rules_count = dict(zip(STRONG_RULES, [0] * len(STRONG_RULES)))

    # Analysis statistics
    # Keep track of how many reports were attempted to be analysed
    attempted_report_analysis = 0
    # Keep track of how many reports were analysed
    num_analysed_reports = 0
    # Keep track of the CVEs where there is no report file
    reports_not_found = []

    for record in tqdm(dataset, total=len(dataset), desc="Analysing Records"):
        # ID;URL;VERSIONS;FLAG;COMMITS;COMMENTS
        cve_id = record[0]
        fixing_commits = record[4].split(",")

        attempted_report_analysis += 1

        try:
            with open(
                f"{PROSPECTOR_REPORT_PATH}{filename}/{cve_id}.json"
            ) as file:
                # Get all commit IDs present in the report
                report_data = json.load(file)

        except FileNotFoundError:
            reports_not_found.append(cve_id)
            logger.debug(f"Couldn't find report for {cve_id}")
            continue

        num_analysed_reports += 1

        true_fixing_commits_in_report = get_true_fixing_commits_in_report(
            report_data=report_data,
            fixing_commits=fixing_commits,
        )

        # Fixing commit is not among the ranked commits of the report
        if len(true_fixing_commits_in_report) == 0:
            fixing_commit_not_found += 1
            logger.debug(
                f"Report for {cve_id} does not contain fixing commit at all."
            )
            continue

        if len(true_fixing_commits_in_report) > 0:
            fixing_commit_found += 1

        #### Find the confidence & count strong rules
        for i, commit in enumerate(report_data["commits"]):
            logger.debug(
                f"index: {i}, number of commits: {len(report_data['commits'])}"
            )
            # First commit is fixing commit
            if i == 0:
                matched_rules = [rule["id"] for rule in commit["matched_rules"]]
                # logger.debug(f"Matched rules: {matched_rules}") # Sanity Check
                for matched_rule in matched_rules:
                    if matched_rule in STRONG_RULES:
                        strong_rules_count[matched_rule] += 1
                        confidence["high"].append((cve_id, matched_rule))
                        break

                    if matched_rule in WEAK_RULES:
                        confidence["medium"].append((cve_id, matched_rule))
                        break
                break

            # Fixing commit among the first 10
            if i > 0 and i < 10 and commit["commit_id"] in fixing_commits:
                confidence["low"].append(cve_id)
                break

            # Commit not among the first 10
            if i >= 10:
                fixing_commit_not_among_10 += 1
                break

    #### Table Data (write to table)
    logger.info(f"strong rules count: {strong_rules_count}")
    table_data = []
    # Add first row of high confidence
    table_data.append(
        [
            len(confidence["high"]),
            round(len(confidence["high"]) / num_analysed_reports * 100, 2),
        ]
    )
    for _, v in strong_rules_count.items():
        table_data.append([v, round(v / num_analysed_reports * 100, 2)])
    table_data.append(
        [
            len(confidence["medium"]),
            round(len(confidence["medium"]) / num_analysed_reports * 100, 2),
        ]
    )
    table_data.append(
        [
            len(confidence["low"]),
            round(len(confidence["low"]) / num_analysed_reports * 100, 2),
        ]
    )
    table_data.append(
        [
            fixing_commit_not_among_10,
            round(fixing_commit_not_among_10 / num_analysed_reports * 100, 2),
        ]
    )
    table_data.append(
        [
            fixing_commit_not_found,
            round(fixing_commit_not_found / num_analysed_reports * 100, 2),
        ]
    )
    table_data.append([0, 0.0])

    update_summary_execution_table(
        "MVI",
        table_data,
        str(num_analysed_reports),
        f"{ANALYSIS_RESULTS_PATH}summary_execution_results.tex",
    )

    logger.info(
        f"Analysed {num_analysed_reports}, couldn't find reports for {len(reports_not_found)} out of {attempted_report_analysis} analysis attempts."
    )
    logger.info(
        f"Fixing commit among ranked commits in report: {fixing_commit_found}"
    )
    logger.info(
        f"Fixing commit not among ranked commits in report: {fixing_commit_not_found}"
    )
    logger.info(
        f"Found {len(confidence['high'])} commits with high confidence, {len(confidence['medium'])} commits with medium confidence and {len(confidence['low'])} commits with low confidence."
    )
    logger.debug(f"Strong rules matching: {confidence['high']}")
    logger.debug(f"Weak rules matching: {confidence['medium']}")
    logger.debug(
        f"Fixing commit among first 10 (low conf): {confidence['low']}"
    )


def get_true_fixing_commits_in_report(
    report_data,
    fixing_commits: List[str],
):
    """Return the list of true fixing commits mentioned in the Prospector
    report.
    """
    ranked_candidates = [
        commit["commit_id"] for commit in report_data["commits"]
    ]

    true_fixing_commits_in_report = [
        commit for commit in ranked_candidates if commit in fixing_commits
    ]

    return true_fixing_commits_in_report


def update_confidence_and_strong_rules(
    i: int,
    commit,
    cve_id,
    fixing_commits: List,
    confidence: dict[List],
    strong_rules_count,
):
    matched_rules = [rule["id"] for rule in commit["matched_rules"]]
    # logger.debug(f"Matched rules: {matched_rules}") # Sanity Check

    # Fixing commit among the first 10
    if i > 0 and commit["commit_id"] in fixing_commits:
        confidence["low"].append(cve_id)
        return confidence, strong_rules_count

    # First commit is fixing commit
    if i == 0:
        for matched_rule in matched_rules:
            if matched_rule in STRONG_RULES:
                strong_rules_count[matched_rule] += 1
                confidence["high"].append((cve_id, matched_rule))
                return confidence, strong_rules_count

            if matched_rule in WEAK_RULES:
                confidence["medium"].append((cve_id, matched_rule))
                return confidence, strong_rules_count


def analyze_prospector(filename: str):  # noqa: C901
    """Analyses Prospector's reports."""

    file = INPUT_DATA_PATH + filename + ".csv"
    dataset = load_dataset(file)

    missing = []
    skipped = 0

    results = {
        "COMMIT_IN_REFERENCE": set(),
        "CVE_ID_IN_MESSAGE": set(),
        "CVE_ID_IN_LINKED_ISSUE": set(),
        "CROSS_REFERENCE": set(),
        "medium_confidence": set(),
        "low_confidence": set(),
        "not_found": set(),
        "not_reported": set(),  # Commit does not appear in the report
        "false_positive": set(),
        "real_false_positive": set(),
    }
    rulescount = defaultdict(lambda: 0)

    # For each CSV in the input dataset, check its report
    logger.info("Checking reports")
    for itm in dataset:
        try:
            (
                is_fix,
                has_certainty,
                commit_id,
                exists,
                position,
                ranks,
                rules,
            ) = check_report(
                PROSPECTOR_REPORT_PATH + filename, itm[0], itm[4]
            )  # ID;URL;VERSIONS;FLAG;COMMITS;COMMENTS

            results, rulescount, skipped = write_matched_rules(
                results,
                rulescount,
                skipped,
                itm,
                is_fix,
                has_certainty,
                commit_id,
                exists,
                position,
                ranks,
                rules,
            )

        except FileNotFoundError:
            print(f"No report for {itm[0]}")
            continue

    print("Saved results to matched_rules.tex")
    logger.debug(f"Count for each rule: {rulescount}")
    # print(
    #     ",".join(
    #         results["not_reported"]
    #         | results["not_found"]
    #         | results["false_positive"]
    #         | results["low_confidence"]
    #         | results["medium_confidence"]
    #         | results["CVE_ID_IN_LINKED_ISSUE"]
    #         | results["CROSS_REFERENCE"]
    #         | results["CVE_ID_IN_MESSAGE"]
    #     )
    # )

    total = len(dataset) - skipped
    logger.debug(f"Analysed {total} reports.")
    rulescount = dict(sorted(rulescount.items()))

    make_rules_plot(rulescount)

    # Save the results to the Latex table
    table_data_categories = []
    # Calculate the sum of high confidence results: COMMIT_IN_REFERENCE + CVE_ID_IN_MESSAGE + CVE_ID_IN_LINKED_ISSUE + CROSS_REFERENCE
    num_high_confidence = sum(
        [
            len(v)
            for k, v in results.items()
            if k
            in [
                "CVE_ID_IN_MESSAGE",
                "CVE_ID_IN_LINKED_ISSUE",
                "CROSS_REFERENCE",
                "COMMIT_IN_REFERENCE",
            ]
        ]
    )
    # First row
    table_data_categories.append(
        [num_high_confidence, round(num_high_confidence / total * 100, 2)]
    )
    # Middle rows
    for key, value in results.items():
        logger.debug(
            f"Key: {key}, Length of value: {len(value)}"
        )  # Sanity Check
        table_data_categories.append(
            [len(value), round(len(value) / total * 100, 2)]
        )

    update_summary_execution_table(
        "MVI",
        table_data_categories,
        str(total),
        f"{ANALYSIS_RESULTS_PATH}summary_execution_results.tex",
    )

    total_check = sum([len(x) for x in results.values()])
    print(f"\nAnalysed {total_check} reports")  # Sanity Check

    if total_check != total:
        print("ERROR: Some CVEs are missing")

    return missing


def build_table_row(matched_rules):
    rules_list = [
        "COMMIT_IN_REFERENCE",
        "CVE_ID_IN_MESSAGE",
        "CVE_ID_IN_LINKED_ISSUE",
        "CROSS_REFERENCED_JIRA_LINK",
        "CROSS_REFERENCED_GH_LINK",
        "CHANGES_RELEVANT_FILES",
        "CHANGES_RELEVANT_CODE",
        "RELEVANT_WORDS_IN_MESSAGE",
        "ADV_KEYWORDS_IN_FILES",
        "ADV_KEYWORDS_IN_MSG",
        "SEC_KEYWORDS_IN_MESSAGE",
        "SEC_KEYWORDS_IN_LINKED_GH",
        "SEC_KEYWORDS_IN_LINKED_JIRA",
        "GITHUB_ISSUE_IN_MESSAGE",
        "JIRA_ISSUE_IN_MESSAGE",
        "COMMIT_HAS_TWINS",
    ]
    out = []
    for id in rules_list:
        if id in matched_rules:
            out.append("/checkmark")
        else:
            out.append("")
    return out


def write_matched_rules(
    results: dict,
    rulescount,
    skipped,
    itm,
    is_fix,
    has_certainty,
    commit_id,
    exists,
    position,
    ranks,
    rules,
):
    with open(ANALYSIS_RESULTS_PATH + "matched_rules.tex", "a+") as f:
        # if the commit doesn't exist?
        if not is_fix and not exists and position < 0:
            skipped += 1
            return results, rulescount, skipped

        # Commit is not reported (in the whole report, the fixing commit doesn't show up)
        if not is_fix and not has_certainty and commit_id and position < 0:
            results["not_reported"].add(itm[0])
            logger.debug(f"Commit was not reported: {itm[0]}")
            return results, rulescount, skipped

        # False positives
        if not is_fix and has_certainty:
            results["false_positive"].add(itm[0])
            update_false_positives(itm)
            logger.debug(
                f"Commit {itm[0]} was a false positive (high confidence but not fixing commit)."
            )
            return results, rulescount, skipped

        # Commit not found (commit was not in the first 10 ranked candidates of the report)
        if is_fix and not has_certainty and position >= 10:
            results["not_found"].add(itm[0])

        # Commit is fixing commit and has certainty
        if is_fix and has_certainty:  # and 0 <= position < 10:
            f.write(
                f"{itm[0]} & {' & '.join(build_table_row(rules))} & {' & '.join([str(x) for x in ranks]).replace('-1', '')} \\\\ \\midrule\n"
            )

            results[has_certainty].add(itm[0])

        elif is_fix and not has_certainty and position == 0:
            f.write(
                f"{itm[0]} & {' & '.join(build_table_row(rules))} & {' & '.join([str(x) for x in ranks]).replace('-1', '')} \\\\ \\midrule\n"
            )
            results["medium_confidence"].add(itm[0])

        elif is_fix and not has_certainty and 0 < position < 10:
            results["low_confidence"].add(itm[0])
            f.write(
                f"{itm[0]} & {' & '.join(build_table_row(rules))} & {' & '.join([str(x) for x in ranks]).replace('-1', '')} \\\\ \\midrule\n"
            )

        for rule in rules:
            rulescount[rule] += 1
            if results.get(rule, None):
                results[rule].add(commit_id)

    return results, rulescount, skipped


def make_rules_plot(rulescount):
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams["savefig.dpi"] = 300
    sns.set_style("whitegrid")
    colors = [
        (
            "#ffa600"
            if id
            in (
                "COMMIT_IN_REFERENCE",
                "CROSS_REFERENCED_GH_LINK",
                "CROSS_REFERENCED_JIRA_LINK",
                "CVE_ID_IN_LINKED_ISSUE",
                "CVE_ID_IN_MESSAGE",
            )
            else "#003f5c"
        )
        for id in rulescount.keys()
    ]
    ss = sns.barplot(
        x=list(rulescount.keys()),
        y=list(rulescount.values()),
        hue=list(rulescount.keys()),
        palette=colors,
        width=0.6,
        legend=False,
    )
    plt.xticks(rotation="vertical")
    # ss.set_xscale("log", base=2)
    # ss.set_xticks([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
    # ss.set_xticklabels([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024], rot)

    # ss.set_xticks(range(0, 800, 100))
    ss.tick_params(axis="x", labelsize=8)
    # plt.show()
    plt.savefig(f"{ANALYSIS_RESULTS_PATH}plots/project-kb.png")

    # for rule, count in rulescount.items():
    #     print(f"{rule}: {count}") # Sanity Check


def sum_relevances(list_of_rules):
    """Calculates the sum of relevance scores for a list of matched rules."""
    return sum([r["relevance"] for r in list_of_rules])


def check_report_get_rules(dataset, cve, fixing_commits):
    """Retrieves the matched rules and commit information for a given CVE and a
    list of fixing commits.

    Args:
        dataset (str): The path to the dataset directory.
        cve (str): The CVE identifier.
        fixing_commits (list): A list of commit IDs that are fixing the vulnerability.

    Returns:
        tuple: A tuple containing the following elements:
            - A list of matched rule IDs
            - The position (index) of the fixing commit in the list of commits
            - The sum of relevance scores for the matched rules
            - The commit ID of the fixing commit
    """
    with open(f"{dataset}/{cve}.json", "r") as file:
        data = json.load(file)
        # not_fixing = [
        #     commit
        #     for commit in data["commits"]
        #     if commit["commit_id"] not in fixing_commits
        # ]
        # if len(not_fixing) == 0:
        #     return [], 0, 0, 0
        # return (
        #     [r["id"] for r in not_fixing[0]["matched_rules"]],
        #     1,
        #     1,
        #     not_fixing[0]["commit_id"],
        # )
        for i, commit in enumerate(data["commits"]):
            if commit["commit_id"] in fixing_commits:
                return (
                    [r["id"] for r in commit["matched_rules"]],
                    i + 1,
                    sum_relevances(commit["matched_rules"]),
                    commit["commit_id"],
                )

            if "twins" in commit:
                for twin in commit["twins"]:
                    if twin[1] in fixing_commits:
                        return (
                            [r["id"] for r in commit["matched_rules"]],
                            i + 1,
                            sum_relevances(commit["matched_rules"]),
                            commit["commit_id"],
                        )
            # return (
            #     [r["id"] for r in commit["matched_rules"]],
            #     i + 1,
            #     sum_relevances(commit["matched_rules"]),
            #     commit["commit_id"],
            # )
    return None, None, None, None


def has_certainty(rules: List[Dict]):
    """Checks if a list of matched rules contains any strong (high-certainty) rules."""
    if any(rule["id"] == "COMMIT_IN_REFERENCE" for rule in rules):
        return "COMMIT_IN_REFERENCE"
    if any(rule["id"] == "VULN_ID_IN_MESSAGE" for rule in rules):
        return "CVE_ID_IN_MESSAGE"
    if any(rule["id"] in ("XREF_BUG", "XREF_GH") for rule in rules):
        return "CROSS_REFERENCE"
    if any(rule["id"] == "VULN_ID_IN_LINKED_ISSUE" for rule in rules):
        return "CVE_ID_IN_LINKED_ISSUE"

    return False


def get_first_commit_relevance(data):
    if len(data["commits"]) == 0:
        return -1
    else:
        return sum_relevances(data["commits"][0]["matched_rules"])


def is_fixing_commit(commit, fixing_commits):
    """Returns whether a commit is in a list of true fixing commits."""
    return commit["commit_id"] in fixing_commits or any(
        twin[1] in fixing_commits for twin in commit.get("twins", [])
    )


def get_commit_info(commit, index, relevance_first_commit, relevance_next):
    return (
        True,
        has_certainty(commit["matched_rules"]),
        commit["commit_id"],
        True,
        index,
        [
            index + 1,
            sum_relevances(commit["matched_rules"]),
            relevance_first_commit,
            relevance_next,
        ],
        [r["id"] for r in commit["matched_rules"]],
    )


def get_non_fixing_commit_info(commit, index, score_first):
    cert = has_certainty(commit["matched_rules"])
    if cert != 0:
        return (
            False,
            cert,
            commit["commit_id"],
            True,
            index,
            [
                sum_relevances(commit["matched_rules"]),
                score_first,
                -1,
            ],
            [r["id"] for r in commit["matched_rules"]],
        )
    return None


def check_report(dataset, cve, fixing_commits):
    """This function checks the report for a given CVE and list of fixing commits.

    Args:
        dataset (str): The path to the dataset directory.
        cve (str): The CVE identifier.
        fixing_commits (list): A list of commit IDs that are fixing the vulnerability.

    Returns:
        tuple: A tuple containing the following elements:
        - A boolean indicating if the commit is a fixing commit
        - The certainty level of the matched rules (a string or 0)
        - The commit ID (or None if no commit is found)
        - A boolean indicating if the commit exists
        - The position (index) of the commit (-1 if no commit is found)
        - A list containing the position, relevance score, score_first, and relevance_next (or None if no commit is found)
        - A list of matched rule IDs
    """
    try:
        with open(f"{dataset}/{cve}.json", "r") as file:
            data = json.load(file)

            relevance_first_commit = get_first_commit_relevance(data)
            logger.debug(f"{cve}")
            logger.debug(f"Score first: {relevance_first_commit}")

            for index, commit in enumerate(data["commits"]):
                relevance_next = -1
                if index > 0:
                    relevance_next = sum_relevances(
                        data["commits"][index - 1]["matched_rules"]
                    )

                if is_fixing_commit(commit, fixing_commits):
                    if index == 0:
                        relevance_first_commit = -1
                    commit_info = get_commit_info(
                        commit, index, relevance_first_commit, relevance_next
                    )
                    logger.debug(f"Fixing Commit Info: {commit_info}")

                    return commit_info

            for index, commit in enumerate(data["commits"]):
                commit_info = get_non_fixing_commit_info(
                    commit, index, relevance_first_commit
                )
                if commit_info:
                    logger.debug(f"Non-fixing Commit Info: {commit_info}")
                    return commit_info

        return (False, 0, True, True, -1, None, [])

    except FileNotFoundError:
        return False, 0, None, False, -1, None, []


def process_json_report(dataset, cve, commits):
    """This function processes the JSON report for a given CVE and list of commits.

    Args:
        dataset (str): The path to the dataset directory.
        cve (str): The CVE identifier.
        commits (list): A list of commit IDs.

    Returns:
        tuple: A tuple containing the following elements:
            - A boolean indicating if the commit exists
            - A list containing the following elements:
                - The CVE ID
                - The position (index) of the commit
                - The sum of relevance scores for the matched rules
                - The number of commits with the same relevance score
                - The sum of relevance scores for the first commit
                - The sum of relevance scores for the next commit with a higher score
    """
    out = []
    exists = True
    try:
        with open(f"{dataset}/{cve}/{cve}.json", "r") as file:
            data = json.load(file)
            processed_commits = {}
            for i, commit in enumerate(data["commits"]):
                processed_commits[commit["commit_id"]] = [
                    sum_relevances(commit["matched_rules"]),
                    i + 1,
                ]

                if commit["commit_id"] in commits:
                    processed_commits.pop(commit["commit_id"])
                    current = [
                        cve,
                        i + 1,
                        sum_relevances(commit["matched_rules"]),
                        None,
                        None,
                        None,
                    ]
                    current[3] = len(
                        [
                            k
                            for k, v in processed_commits.items()
                            if v[0] == current[2]
                        ]
                    )
                    if i > 0:
                        current[4] = sum_relevances(
                            data["commits"][0]["matched_rules"]
                        )
                        r_next = 0
                        for j in range(i, -1, -1):
                            r_next = sum_relevances(
                                data["commits"][j]["matched_rules"]
                            )
                            if r_next > current[2]:
                                current[5] = r_next
                                break
                    out = current
                    exists = True
                    break
    except FileNotFoundError:
        exists = False
    return exists, out


def analyze_rules_usage(dataset_path: str, cve: str = ""):
    """This function analyzes the usage of rules across a dataset."""
    dataset = load_dataset(dataset_path)
    rules: Dict[str, int] = {}
    commit_count = 0
    cve_count = 0
    for itm in dataset:
        cve_count += 1
        with open(f"{dataset_path[:-4]}/{itm[0]}/{itm[0]}.json", "r") as file:
            data = json.load(file)
            for commit in data["commits"]:
                commit_count += 1
                for rule in commit["matched_rules"]:
                    if rule["id"] in rules:
                        rules[rule["id"]] += 1
                    else:
                        rules[rule["id"]] = 1

    sorted_rules = {
        k: v
        for k, v in sorted(
            rules.items(), key=lambda item: item[1], reverse=True
        )
    }
    print(f"\nTotal commits: {commit_count}")
    print(f"Total cves: {cve_count}\n")
    for k, v in sorted_rules.items():
        print(f"{k}: {v}")


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
