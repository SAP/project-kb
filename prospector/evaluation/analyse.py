import csv
import json
import re
import sys
from collections import defaultdict
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import seaborn as sns
from matplotlib import pyplot as plt

from datamodel.advisory import build_advisory_record
from evaluation.dispatch_jobs import (
    INPUT_DATA_PATH,
    PROSPECTOR_REPORT_PATH,
    ANALYSIS_RESULTS_PATH,
    build_table_row,
)
from evaluation.save_results import (
    update_summary_execution_table,
)
from evaluation.utils import load_dataset


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
        "not_reported": set(),
        "false_positive": set(),
        "real_false_positive": set(),
    }
    rulescount = defaultdict(lambda: 0)

    # For each CSV in the input dataset, check its report
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
                results, rulescount, skipped, itm, is_fix, has_certainty, commit_id, exists, position, ranks, rules
            )

        except FileNotFoundError:
            print(f"No report for {itm[0]}")
            continue

    print("Saved results to matched_rules.tex")

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
    rulescount = dict(sorted(rulescount.items()))

    make_rules_plot(rulescount)


    # Save the results to the Latex table
    table_data = []
    for key, value in results.items():
        # print(f"{key}: {len(value)} ({(len(value)/1315)*100:.2f}%)") # Sanity Check
        table_data.append([len(value), len(value) / len(dataset) * 100])

    update_summary_execution_table(
        "MVI",
        table_data,
        f"{ANALYSIS_RESULTS_PATH}summary_execution_results.tex",
    )

    total_check = sum([len(x) for x in results.values()])
    print(f"\nAnalysed {total_check} reports") # Sanity Check

    if total_check != total:
        print("ERROR: Some CVEs are missing")

    return missing


def write_matched_rules(
    results, rulescount, skipped, itm, is_fix, has_certainty, commit_id, exists, position, ranks, rules
):
    with open(ANALYSIS_RESULTS_PATH + 'matched_rules.tex', 'a+') as f:
        if is_fix and has_certainty:  # and 0 <= position < 10:
            f.write(f"{itm[0]} & {' & '.join(build_table_row(rules))} & {' & '.join([str(x) for x in ranks]).replace('-1', '')} \\\\ \\midrule\n")

            results[has_certainty].add(itm[0])

            for rule in rules:
                rulescount[rule] += 1

        elif is_fix and not has_certainty and position == 0:
            f.write(f"{itm[0]} & {' & '.join(build_table_row(rules))} & {' & '.join([str(x) for x in ranks]).replace('-1', '')} \\\\ \\midrule\n")
            results["medium_confidence"].add(itm[0])
            for rule in rules:
                rulescount[rule] += 1

        elif is_fix and not has_certainty and 0 < position < 10:
            results["low_confidence"].add(itm[0])
            f.write(f"{itm[0]} & {' & '.join(build_table_row(rules))} & {' & '.join([str(x) for x in ranks]).replace('-1', '')} \\\\ \\midrule\n")

            for rule in rules:
                rulescount[rule] += 1

        elif is_fix and not has_certainty and position >= 10:
            results["not_found"].add(itm[0])
            for rule in rules:
                rulescount[rule] += 1

        elif not is_fix and has_certainty:
            results["false_positive"].add(itm[0])
            with open(f"{ANALYSIS_RESULTS_PATH}false_postive.txt", "a") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}"]
                )

        elif not is_fix and not has_certainty and commit_id and position < 0:
            results["not_reported"].add(itm[0])
            # print(f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}")

        elif not is_fix and not exists and position < 0:
            skipped += 1

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
        legend=False
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
    """Retrieves the matched rules and commit information for a given CVE and a list of
    fixing commits.

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
    if any(rule["id"] == "CVE_ID_IN_MESSAGE" for rule in rules):
        return "CVE_ID_IN_MESSAGE"
    if any(
        rule["id"] in ("CROSS_REFERENCED_JIRA_LINK", "CROSS_REFERENCED_GH_LINK")
        for rule in rules
    ):
        return "CROSS_REFERENCE"
    if any(rule["id"] == "CVE_ID_IN_LINKED_ISSUE" for rule in rules):
        return "CVE_ID_IN_LINKED_ISSUE"

    return False


def get_first_commit_score(data):
    if len(data["commits"]) == 0:
        return -1
    else:
        return sum_relevances(data["commits"][0]["matched_rules"])


def is_fixing_commit(commit, fixing_commits):
    return commit["commit_id"] in fixing_commits or any(
        twin[1] in fixing_commits for twin in commit.get("twins", [])
    )


def get_commit_info(commit, index, score_first, score_next):
    return (
        True,
        has_certainty(commit["matched_rules"]),
        commit["commit_id"],
        True,
        index,
        [
            index + 1,
            sum_relevances(commit["matched_rules"]),
            score_first,
            score_next,
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
        - A list containing the position, relevance score, score_first, and score_next (or None if no commit is found)
        - A list of matched rule IDs
    """
    try:
        with open(f"{dataset}/{cve}.json", "r") as file:
            data = json.load(file)
            score_first = get_first_commit_score(data)

            for index, commit in enumerate(data["commits"]):
                score_next = -1
                if index > 0:
                    score_next = sum_relevances(
                        data["commits"][index - 1]["matched_rules"]
                    )

                if is_fixing_commit(commit, fixing_commits):
                    if index == 0:
                        score_first = -1
                    return get_commit_info(
                        commit, index, score_first, score_next
                    )

            for index, commit in enumerate(data["commits"]):
                commit_info = get_non_fixing_commit_info(
                    commit, index, score_first
                )
                if commit_info:
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


def is_real_version(text: str):
    return bool(re.match(r"\d+\.(?:\d+\.*)*\d", text))


VULN = ["version", "through", "versions"]

FIXED = [
    "before",
    "before release",
    "before version",
    "prior to",
    "upgrade to",
    "fixed in",
    "fixed in version",
    "fixed in release",
    "to version",
]


def get_version_spacy(text: str, nlp):
    """This function extracts vulnerable and fixed version numbers from a given text using spaCy."""
    doc = nlp(text)
    # relevant_sentences = {}
    # relevant_sentence = ""
    fixed_version = ""
    vulnerable_version = ""
    for i in range(len(doc))[1:]:
        if is_real_version(doc[i].text):
            if doc[i - 1].text in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            elif (doc[i - 2].text + " " + doc[i - 1].text) in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            elif (
                doc[i - 3].text + " " + doc[i - 2].text + " " + doc[i - 1].text
            ) in FIXED:
                # relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            else:
                # relevant_sentence = doc[: i + 1]
                vulnerable_version = doc[i].text
    return vulnerable_version, fixed_version


def check_advisory(cve, repository=None, nlp=None):
    """This function checks the advisory for a given CVE and attempts to extract version information."""
    advisory = build_advisory_record(
        cve, nvd_rest_endpoint="http://localhost:8000/nvd/vulnerabilities/"
    )
    references = [urlparse(r).netloc for r in advisory.references]
    return references
    vuln = "None"
    if len(advisory.versions.get("affected")):
        vuln = advisory.versions.get("affected")[-1]

    fixed = "None"
    if len(advisory.versions.get("fixed")):
        fixed = advisory.versions.get("fixed")[-1]

    vuln2, fixed2 = get_version_spacy(advisory.description, nlp)
    res = [advisory.cve_id, advisory.description]
    if fixed == fixed2 and vuln == vuln2:
        res.append(f"{vuln}:{fixed}")
    if fixed == "None" and fixed2 != "":
        res.append(f"{vuln}:{fixed2}")
    if vuln == "None" and vuln2 != "":
        res.append(f"{vuln2}:{fixed}")
    if fixed != fixed2 and fixed2 != "" and fixed != "None":
        res.append(f"{vuln}:{fixed}")
        res.append(f"{vuln}:{fixed2}")

    if len(res) > 2:
        res.append("***************************************")
        print(advisory.cve_id)
        return res
    else:
        res.append(f"{vuln}:{fixed}")
        res.append("***************************************")
        print(advisory.cve_id)
        return res


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
            print(f"Skipped {itm[0]}.json because file could not be found.")
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

    print(
        # f"Found {len(dataset)} files in input dataset. \n{skipped} reports were missing: {missing}."
        f"Found {len(dataset)} files in input dataset. \n{skipped} reports were missing."
    )

    print("\nIn these reports, the LLM invokation needed the following times:")
    print(f"Average time to get repository URL: \t\t\t\t{avg_repo_time}")
    print(
        f"Average time to get commit classification (single request): \t{avg_cc_time}"
    )
    print(
        f"Average time to get commit classification (all {cc_num_commits} requests): \t{avg_total_cc_time}"
    )


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
            llm_stats = data["processing_statistics"]["LLM"]["llm"][
                "llm_service"
            ]["LLMService"]

            total_cc_time = sum(llm_stats["classify_commit"]["execution time"])

            avg_cc_time = total_cc_time / len(
                llm_stats["classify_commit"]["execution time"]
            )

            return (
                llm_stats["get_repository_url"]["execution time"][0],
                avg_cc_time,
                total_cc_time,
            )

        except Exception:
            print(f"Did not have expected JSON fields: {filepath}.")
            raise ValueError


def get_cc_num_commits(filepath):
    """Returns how many commits the commit classification rule was applied to."""
    with open(filepath, "r") as file:
        data = json.load(file)

        num = len(
            data["processing_statistics"]["LLM"]["llm"]["llm_service"][
                "LLMService"
            ]["classify_commit"]["execution time"]
        )

        return num
