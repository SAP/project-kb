import csv
import json
import re
from collections import defaultdict
from typing import Dict, List
from urllib.parse import urlparse

import seaborn as sns
from matplotlib import pyplot as plt

from datamodel.advisory import build_advisory_record
from evaluation.dispatch_jobs import build_table_row
from evaluation.utils import load_dataset


def analyze_results_rules(dataset_path: str):
    print(dataset_path)
    dataset_path = "empirical_study/datasets/" + dataset_path + ".csv"
    dataset = load_dataset(dataset_path)
    rules = {}
    table = {}
    count = 0
    for itm in dataset:
        try:
            r, i, v, id = check_report_get_rules(dataset_path[:-4], itm[0], itm[4])
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
            print(f"{v[3][0]};{v[3][1]};{v[3][2]};{v[3][3]};{v[3][4]};{v[3][5]}")
            # print(f"{k}: {v[3]}/commit/{v[0]}")


def analyze_prospector(filename: str):  # noqa: C901
    # delete_missing_git(dataset_path)
    # return []
    filename = "empirical_study/datasets/" + filename + ".csv"
    dataset = load_dataset(filename)
    # res_ts = temp_load_reservation_dates(dataset_path[:-4] + "_timestamps.csv")

    missing = []
    skipped = 0
    # timestamps = {
    #     "COMMIT_IN_REFERENCE": list(),
    #     "CVE_ID_IN_MESSAGE": list(),
    #     "CVE_ID_IN_LINKED_ISSUE": list(),
    #     "CROSS_REFERENCE": list(),
    #     "medium_confidence": list(),
    #     "low_confidence": list(),
    # }
    yearly_timestamps = {}
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
    # references = list()

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
                filename[:-4], itm[0], itm[4]
            )  # ID;URL;VERSIONS;FLAG;COMMITS;COMMENTS
        except FileNotFoundError:
            continue

        # year = itm[0].split("-")[1]
        # if is_fix and timestamp is not None:
        #     res_timestamp = get_reservation_date(itm[0])
        #     if res_timestamp is not None:
        #         ts = timestamp - res_timestamp
        #         # if int(ts / 86400) > -900:
        #         year = itm[0].split("-")[1]
        #         if year not in timestamps:
        #             timestamps[year] = []
        #         timestamps[year].append(int(ts / 86400))
        #         # ts_analsis.append(int(ts / 86400))
        #     else:
        #         print(f"Missing reservation date for {itm[0]}")
        #     time.sleep(0.05)
        # if timestamp:

        #     # adv_ts = res_ts.get(itm[0])
        #     timestamp = adv_ts - timestamp
        #     yearly_timestamps.setdefault(year, list())
        #     yearly_timestamps[year].append(int(timestamp / 86400))
        # timestamp = abs(timestamp)

        # if is_fix and position < 10:
        #     rules, _, _, _ = check_report_get_rules(filename[:-4], itm[0], itm[4])
        #     print(itm[0], rules)
        # else:
        #     continue
        # rules, _, _, _ = check_report_get_rules(filename[:-4], itm[0], itm[4])
        # for rule in rules:
        #     rulescount[rule] += 1
        # continue
        if is_fix and has_certainty:  # and 0 <= position < 10:
            print(
                itm[0],
                "&",
                " & ".join(build_table_row(rules)),
                "&",
                " & ".join([str(x) for x in ranks]).replace("-1", ""),
                "\\\\ \\midrule",
            )
            results[has_certainty].add(itm[0])
            # if "COMMIT_IN_REFERENCE" in has_certainty and all(
            #    rule != "COMMIT_IN_REFERENCE"
            #    for rule in has_certainty
            #    if rule != "COMMIT_IN_REFERENCE"
            # ):
            #    with open("only_commit_in_reference2.csv", "a", newline="") as file:
            #        writer = csv.writer(file)
            #        writer.writerow(
            #            [f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}"]
            #        )
            # elif all(rule != "COMMIT_IN_REFERENCE" for rule in has_certainty):
            #    with open("only_other_strong_rules.csv", "a", newline="") as file:
            #        writer = csv.writer(file)
            #        writer.writerow(
            #            [f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}"]
            #        )
            for rule in rules:
                rulescount[rule] += 1
            # print(f"{filename[:-4]}/{itm[0]}.json")
            # print(f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}")
            # print(f"{filename[:-4]}/{itm[0]}.json")
            # timestamps["false_positive"].append(timestamp)
        # elif is_fix and has_certainty and position > 0:
        #     results["real_false_positive"].add(itm[0])
        # if int(timestamp / 86400) < 731:
        #     timestamps[has_certainty].append(int(timestamp / 86400))
        elif is_fix and not has_certainty and position == 0:
            print(
                itm[0],
                "&",
                " & ".join(build_table_row(rules)),
                "&",
                " & ".join([str(x) for x in ranks]).replace("-1", ""),
                "\\\\ \\midrule",
            )
            results["medium_confidence"].add(itm[0])
            for rule in rules:
                rulescount[rule] += 1
            # print(itm[0] + " - " + str(position + 1))

            # if int(timestamp / 86400) < 731:
            #     timestamps["medium_confidence"].append(int(timestamp / 86400))
        elif is_fix and not has_certainty and 0 < position < 10:
            results["low_confidence"].add(itm[0])
            print(
                itm[0],
                "&",
                " & ".join(build_table_row(rules)),
                "&",
                " & ".join([str(x) for x in ranks]).replace("-1", ""),
                "\\\\ \\midrule",
            )
            for rule in rules:
                rulescount[rule] += 1
            # print(itm[0] + " - " + str(position + 1))
            # print(
            #     f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]} pos:{position}"
            # )
            # if int(timestamp / 86400) < 731:
            #     timestamps["low_confidence"].append(int(timestamp / 86400))
            # print(itm[0], position + 1)
        elif is_fix and not has_certainty and position >= 10:
            results["not_found"].add(itm[0])
            for rule in rules:
                rulescount[rule] += 1
            # timestamps["not_found"].append(int(timestamp / 86400))
            # print(itm[0], position + 1)
            # print(f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}")
        elif not is_fix and has_certainty:
            results["false_positive"].add(itm[0])
            with open("false_postive", "a") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}"]
                )
            print(f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}")
        elif not is_fix and not has_certainty and commit_id and position < 0:
            results["not_reported"].add(itm[0])
            print(f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}")
        elif not is_fix and not exists and position < 0:
            skipped += 1
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
        palette=colors,
        width=0.6,
    )
    plt.xticks(rotation="vertical")
    # ss.set_xscale("log", base=2)
    # ss.set_xticks([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
    # ss.set_xticklabels([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024], rot)

    # ss.set_xticks(range(0, 800, 100))
    ss.tick_params(axis="x", labelsize=8)
    # plt.show()
    plt.savefig("project-kb.png")

    for rule, count in rulescount.items():
        print(f"{rule}: {count}")
    # missing_lookup_git(missing)

    # print(YEAR)
    print()
    total_check = sum([len(x) for x in results.values()])
    print(total_check)
    # total_year = sum([len([x for x in y if YEAR in x]) for y in results.values()])
    for key, value in results.items():
        print(f"{key}: {len(value)} ({(len(value)/1315)*100:.2f}%)")
        # print(
        #     f"{key}: {(len([x for x in value if YEAR in x]) / total_year) * 100:.2f}%"
        # )

        # total_check += len(value)
    yearly_timestamps = {k: v for k, v in yearly_timestamps.items() if len(v) > 30}
    # df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in timestamps.items()]))

    # ax = sns.violinplot(df, inner="box")
    # plt.ylabel("Days")
    # plt.show()

    # for key, value in timestamps.items():
    #     print(
    #         f"{key}: mean={int(statistics.mean(value))} stdDev={int(statistics.stdev(value))}"
    #     )

    # df = pd.DataFrame.from_dict(timestamps, orient="index")

    # sns.set(style="whitegrid")
    # sns.violinplot(data=df)

    if total_check != total:
        print("ERROR: Some CVEs are missing")

    return missing


def sum_relevances(list_of_rules):
    return sum([r["relevance"] for r in list_of_rules])


def check_report_get_rules(dataset, cve, fixing_commits):
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
                    return get_commit_info(commit, index, score_first, score_next)

            for index, commit in enumerate(data["commits"]):
                commit_info = get_non_fixing_commit_info(commit, index, score_first)
                if commit_info:
                    return commit_info

        return (False, 0, True, True, -1, None, [])

    except FileNotFoundError:
        return False, 0, None, False, -1, None, []


def process_json_report(dataset, cve, commits):
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
                        [k for k, v in processed_commits.items() if v[0] == current[2]]
                    )
                    if i > 0:
                        current[4] = sum_relevances(data["commits"][0]["matched_rules"])
                        r_next = 0
                        for j in range(i, -1, -1):
                            r_next = sum_relevances(data["commits"][j]["matched_rules"])
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
        k: v for k, v in sorted(rules.items(), key=lambda item: item[1], reverse=True)
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
