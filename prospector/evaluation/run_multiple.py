# flake8: noqa
import argparse
import csv
import json
import multiprocessing
import os
import re
import signal
import subprocess
import sys
import time
from collections import OrderedDict, defaultdict
from distutils.util import strtobool
from typing import Dict, List
from urllib.parse import urlparse

import pandas as pd
import requests
import seaborn as sns
import spacy
from dateutil.parser import isoparse
from matplotlib import pyplot as plt
from tqdm import tqdm

from core.prospector import prospector
from core.report import generate_report
from datamodel.advisory import build_advisory_record
from datamodel.nlp import extract_affected_filenames, get_names
from git.git import Git
from git.version_to_tag import get_possible_tags


def load_dataset(path: str):
    with open(path, "r") as file:
        reader = csv.reader(file, delimiter=";")
        return [row for row in reader if "CVE" in row[0] and row[3] != "True"]


def is_missing(path: str):
    return not os.path.exists(path)


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


# def commit_distance_to_adv(dataset_path: str):
#     dataset = load_dataset(dataset_path)
#     for itm in dataset:


def get_full_commit_ids(dataset_path: str):
    dataset = load_dataset("empirical_study/datasets/" + dataset_path + ".csv")
    for itm in dataset:
        repository = Git(itm[1], "/sapmnt/home/I586140/intern/gitcache")
        commits = []
        for commit in itm[4].split(","):
            commit_id = repository.find_commit(commit)
            if commit_id is not None:
                commits.append(commit_id)

        print(f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{','.join(commits)};{itm[5]}")


def check_version_to_tag_matching(dataset_path: str):
    dataset = load_dataset(dataset_path)
    for itm in dataset:
        repository = Git(itm[1], "/sapmnt/home/I586140/intern/gitcache")
        tags = repository.get_tags()

        prev_version, next_version = itm[2].split(":")
        prev_tag, next_tag = get_possible_tags(tags, itm[2])
        if prev_tag != "" and next_tag != "":
            continue

        if prev_tag == "" and next_tag == "":
            print(
                f"{itm[0]}\n {prev_version}:{next_version}\n{tags}\n*****************\n"
            )
            continue
        if prev_tag == "":
            print(
                f"{itm[0]}\n {prev_version}:{next_tag}OK\n{tags}\n*****************\n"
            )
            continue
        if next_tag == "":
            print(
                f"{itm[0]}\n {prev_tag}OK:{next_version}\n{tags}\n*****************\n"
            )
            continue

        # print(f"{itm[0]}\n{tags}\n")
        # if prev_tag == "":
        #     print(f"{prev_version} -> {tags}")

        # if next_tag == "":
        #     print(f"{next_version} -> {tags}")


def get_reservation_date(cve_id: str):
    # time.sleep(0.05)
    url = f"https://cveawg.mitre.org/api/cve/{cve_id}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            date = response.json()["cveMetadata"]["dateReserved"]
            return cve_id, int(isoparse(date).timestamp())
        except KeyError:
            return None


def temp_load_reservation_dates(dataset_path: str):
    with open(dataset_path, "r") as file:
        reader = csv.reader(file, delimiter=";")
        return {itm[0]: int(itm[1]) for itm in reader}


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
            out.append("\checkmark")
        else:
            out.append("")
    return out


def analyze_prospector(filename: str):  # noqa: C901
    # delete_missing_git(dataset_path)
    # return []
    filename = "empirical_study/datasets/" + filename + ".csv"
    dataset = load_dataset(filename)
    # res_ts = temp_load_reservation_dates(dataset_path[:-4] + "_timestamps.csv")

    missing = []
    skipped = 0
    timestamps = {
        "COMMIT_IN_REFERENCE": list(),
        "CVE_ID_IN_MESSAGE": list(),
        "CVE_ID_IN_LINKED_ISSUE": list(),
        "CROSS_REFERENCE": list(),
        "medium_confidence": list(),
        "low_confidence": list(),
    }
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
    references = list()

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

        year = itm[0].split("-")[1]
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


def delete_missing_git(dataset_path):
    dataset = load_dataset(dataset_path)
    for itm in dataset[:500]:
        repository = Git(itm[1], "/sapmnt/home/I586140/intern/gitcache")
        existing = []
        for commit in itm[4].split(","):
            raw = repository.get_commit(commit)
            try:
                raw.extract_timestamp()
                existing.append(commit)
            except Exception:
                pass
        if len(itm[4].split(",")) != len(existing):
            if len(existing) > 0:
                print(
                    f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{','.join(existing)};{itm[5]}"
                )
        else:
            print(f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{itm[4]};{itm[5]}")


def missing_lookup_git(missing: List[str]):
    count = 0
    for itm in missing:
        cve, repo, versions, _, commits, _ = itm.split(";")
        repository = Git(repo, "/sapmnt/home/I586140/intern/gitcache")
        # repository.clone()

        repo_tags_o = repository.get_tags()
        repo_tags = get_possible_tags(repo_tags_o, versions)
        if repo_tags[0] is None and repo_tags[1] is None:
            continue
        versions = versions.split(":")
        print(f"{cve}")

        print(f"Vers: {versions}")
        print(f"Tags: {repo_tags}")
        existing = []
        flag = False
        for commit in commits.split(","):
            raw_commit = repository.get_commit(commit)
            if raw_commit.exists():
                existing.append(commit)

            # if len(commits.split(",")) != len(existing):
            #     if len(existing) > 0:
            #         print(f"{cve};{repo};{versions};False;{','.join(existing)};")
            #     else:
            #         pass
            #     count += 1

            try:
                raw_commit.tags = raw_commit.find_tags()

                if repo_tags[0] in raw_commit.tags:
                    print(
                        repo + "/commit/" + raw_commit.id,
                        " - ",
                        "Vulnerable tag is fixed",
                    )
                elif (
                    repo_tags[1] in raw_commit.tags
                    and repo_tags[0] not in raw_commit.tags
                ):
                    commit_ts = raw_commit.get_timestamp()
                    next_tag_ts = repository.get_timestamp(repo_tags[1], "a")
                    prev_tag_ts = repository.get_timestamp(repo_tags[0], "a")
                    if prev_tag_ts < commit_ts < next_tag_ts:
                        print(repo + "/commit/" + raw_commit.id, " - ", "Weird")
                        print(
                            f"python client/cli/main.py {cve} --repository {repo} --version-interval {repo_tags[0]}:{repo_tags[1]}"
                        )
                    else:
                        print("Commit timestamp is outside the time interval")
                elif repo_tags[1] not in raw_commit.tags:
                    if not flag:
                        print("simola")
                        flag = True
                    print(repo + "/commit/" + raw_commit.id)
                    ttags = [t for t in raw_commit.tags if repo_tags[1][:3] == t[:3]]
                    print(ttags)
                if raw_commit.tags == []:
                    print(repo + "/commit/" + raw_commit.id, " - ", "No tags")
            except Exception:
                print(repo + "/commit/" + raw_commit.id, " - ", "Commit not found")

        print("=====================================")
    # print(f"Mismatch: {count}/{len(missing)}")


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


def check_report(dataset, cve, fixing_commits):
    try:
        with open(f"{dataset}/{cve}.json", "r") as file:
            data = json.load(file)
            adv_timestamp = int(data["advisory_record"]["published_timestamp"])
            # for i in data["advisory_record"]["references"]:
            #     if "commit::" not in i:
            #         print(i)
            # adv_timestamp = get_reservation_date(cve)
            if len(data["commits"]) == 0:
                score_first = -1
            else:
                score_first = sum_relevances(data["commits"][0]["matched_rules"])
            for index, commit in enumerate(data["commits"]):
                score_next = -1
                if index > 0:
                    score_next = sum_relevances(
                        data["commits"][index - 1]["matched_rules"]
                    )
                if commit["commit_id"] in fixing_commits:
                    if index == 0:
                        score_first = -1

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

                if "twins" in commit:
                    for twin in commit["twins"]:
                        if twin[1] in fixing_commits:
                            if index == 0:
                                score_first = -1
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

            for index, commit in enumerate(data["commits"]):
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
        return (
            False,
            0,
            True,
            True,
            -1,
            None,
            [],
        )
    except FileNotFoundError:
        # is_fix, has_certainty, commit_id, exists, index
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


def update_comparison_table(dataset):
    data = load_dataset(dataset)
    pass


def to_latex_table():
    data = load_dataset("results/scalco.csv")
    for e in data:
        print(f"{e[0]} & {e[1][19:]} & {e[5]} \\\\  \hline")


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
    relevant_sentences = {}
    relevant_sentence = ""
    fixed_version = ""
    vulnerable_version = ""
    for i in range(len(doc))[1:]:
        if is_real_version(doc[i].text):
            if doc[i - 1].text in FIXED:
                relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            elif (doc[i - 2].text + " " + doc[i - 1].text) in FIXED:
                relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            elif (
                doc[i - 3].text + " " + doc[i - 2].text + " " + doc[i - 1].text
            ) in FIXED:
                relevant_sentence = doc[: i + 1]
                fixed_version = doc[i].text
            else:
                relevant_sentence = doc[: i + 1]
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


def parse_cli_args(args):
    parser = argparse.ArgumentParser(description="Prospector scripts")

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Input file",
    )

    parser.add_argument(
        "-e",
        "--execute",
        action="store_true",
        help="Input file",
    )

    parser.add_argument(
        "-a",
        "--analyze",
        action="store_true",
        help="Input file",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file",
    )

    parser.add_argument(
        "-r",
        "--rules",
        action="store_true",
        help="Rules analysis option",
    )

    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        help="Folder to analyze",
    )

    parser.add_argument(
        "-c",
        "--cve",
        type=str,
        default="",
        help="CVE to analyze",
    )

    parser.add_argument(
        "-p",
        "--parallel",
        help="Run in parallel on multiple CVEs",
        action="store_true",
    )
    return parser.parse_args()


def main(argv):
    args = parse_cli_args(argv)
    if args.execute and not args.analyze and not args.parallel:
        # get_full_commit_ids(args.input)
        # return
        execute_prospector(args.input, args.cve)
    elif args.execute and not args.analyze and args.parallel:
        while not parallel_execution(args.input):
            pass
        # parallel_execution(args.input)
    elif args.analyze and not args.rules and not args.execute:
        analyze_prospector(args.input)
    elif args.analyze and args.rules and not args.execute:
        analyze_results_rules(args.input)
    elif args.analyze and args.execute:
        sys.exit("Choose either to execute or analyze")


def mute():
    sys.stdout = open(os.devnull, "w")


def parallel_execution(filename: str):
    print("Executing in parallel")
    print(os.getcwd())
    dataset = load_dataset("empirical_study/datasets/" + filename + ".csv")
    inputs = [
        {
            "vulnerability_id": cve[0],
            "repository_url": cve[1],
            "version_interval": cve[2],
            "git_cache": "/sapmnt/home/I586140/intern/gitcache",
            "limit_candidates": 2500,
            "filename": filename,
            "silent": True,
        }
        for cve in dataset
        if not os.path.exists(f"empirical_study/datasets/{filename}/{cve[0]}.json")
    ]
    if len(inputs) == 0:
        return True
    try:
        pool = multiprocessing.Pool(processes=4)
        for _ in tqdm(
            pool.imap_unordered(execute_prospector_wrapper, inputs),
            total=len(inputs),
        ):
            pass
        pool.close()
        return True
    except Exception:
        pool.terminate()
        return False


def execute_prospector_wrapper(kwargs):
    filename = kwargs["filename"]
    del kwargs["filename"]
    r, a = prospector(**kwargs)
    if r is not None:
        generate_report(r, a, "json", f"empirical_study/datasets/{filename}/{a.cve_id}")


def execute_prospector(filename: str, cve: str = ""):
    dataset = load_dataset("empirical_study/datasets/" + filename + ".csv")
    if len(cve) != 0:
        dataset = [c for c in dataset if c[0] in cve]

    for cve in dataset:
        if os.path.exists(f"empirical_study/datasets/{filename}/{cve[0]}.json"):
            continue
        print(
            f"\n\n*********\n {cve[0]} ({dataset.index(cve)+1}/{len(dataset)})\n**********\n"
        )
        start_time = time.time()
        result, advisory = prospector(
            vulnerability_id=cve[0],
            repository_url=cve[1],
            version_interval=cve[2],
            git_cache="/sapmnt/home/I586140/intern/gitcache",
            # git_cache="/users/sach/gitcache",
            limit_candidates=2000,
        )

        if result is not None and time.time() - start_time < 1900:
            # result = result[:10]
            # for r in result:
            #     r.relevance = 0
            # r.matched_rules = []
            # advisory.files = []
            # advisory.keywords = []
            # result.sort(key=lambda x: x.timestamp, reverse=False)
            generate_report(
                result,
                advisory,
                "json",
                f"empirical_study/datasets/{filename}/{cve[0]}",
            )


def list_dir_and_select_folder():
    files = [file for file in os.listdir("datasets/") if "." not in file]
    for i, file in enumerate(files):
        print(i, ")", file)
    choice = int(input("Choose a dataset: "))
    return files[choice]


def list_dir_and_select_dataset():
    files = [file for file in os.listdir("datasets/") if file.endswith(".csv")]
    for i, file in enumerate(files):
        print(i, ")", file)
    choice = int(input("Choose a dataset: "))
    return files[choice]


# this method handls ctrl+c from the keyboard to stop execution
def sig_handler(signum, frame):
    print("You pressed Ctrl+C!")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sig_handler)
    main(sys.argv[1:])
