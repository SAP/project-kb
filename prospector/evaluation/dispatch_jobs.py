import csv
import multiprocessing
import os
from typing import List, Optional

import redis
import requests
from dateutil.parser import isoparse
from rq import Connection, Queue
from rq.job import Job
from tqdm import tqdm

from core.prospector import prospector
from core.report import generate_report
from evaluation.utils import (
    INPUT_DATA_PATH,
    PROSPECTOR_REPORT_PATH,
    load_dataset,
    logger,
    evaluation_config,
)
from git.git import Git
from git.version_to_tag import get_possible_tags
from llm.llm_service import LLMService
from util.config_parser import parse_config_file

# get the redis server url
config = parse_config_file()
# redis_url = config.redis_url
backend = config.backend

redis_url = "redis://localhost:6379/0"
# print("redis url: ", redis_url)
# print("redis url: ", backend)


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

        print(
            f"{itm[0]};{itm[1]};{itm[2]};{itm[3]};{','.join(commits)};{itm[5]}"
        )


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


# def missing_lookup_git(missing: List[str]):
#     # count = 0
#     for itm in missing:
#         cve, repo, versions, _, commits, _ = itm.split(";")
#         repository = Git(repo, "/sapmnt/home/I586140/intern/gitcache")
#         # repository.clone()

#         repo_tags_o = repository.get_tags()
#         repo_tags = get_possible_tags(repo_tags_o, versions)
#         if repo_tags[0] is None and repo_tags[1] is None:
#             continue
#         versions = versions.split(":")
#         # print(f"{cve}")

#         print(f"Vers: {versions}")
#         print(f"Tags: {repo_tags}")
#         existing = []
#         flag = False
#         for commit in commits.split(","):
#             raw_commit = repository.get_commit(commit)
#             if raw_commit.exists():
#                 existing.append(commit)

#             # if len(commits.split(",")) != len(existing):
#             #     if len(existing) > 0:
#             #         print(f"{cve};{repo};{versions};False;{','.join(existing)};")
#             #     else:
#             #         pass
#             #     count += 1

#             try:
#                 raw_commit.tags = raw_commit.find_tags()

#                 if repo_tags[0] in raw_commit.tags:
#                     print(
#                         repo + "/commit/" + raw_commit.id,
#                         " - ",
#                         "Vulnerable tag is fixed",
#                     )
#                 elif (
#                     repo_tags[1] in raw_commit.tags
#                     and repo_tags[0] not in raw_commit.tags
#                 ):
#                     commit_ts = raw_commit.get_timestamp()
#                     next_tag_ts = repository.get_timestamp(repo_tags[1], "a")
#                     prev_tag_ts = repository.get_timestamp(repo_tags[0], "a")
#                     if prev_tag_ts < commit_ts < next_tag_ts:
#                         print(repo + "/commit/" + raw_commit.id, " - ", "Weird")
#                         print(
#                             f"python client/cli/main.py {cve} --repository {repo} --version-interval {repo_tags[0]}:{repo_tags[1]}"
#                         )
#                     else:
#                         print("Commit timestamp is outside the time interval")
#                 elif repo_tags[1] not in raw_commit.tags:
#                     if not flag:
#                         print("simola")
#                         flag = True
#                     print(repo + "/commit/" + raw_commit.id)
#                     ttags = [t for t in raw_commit.tags if repo_tags[1][:3] == t[:3]]
#                     print(ttags)
#                 if raw_commit.tags == []:
#                     print(repo + "/commit/" + raw_commit.id, " - ", "No tags")
#             except Exception:
#                 print(repo + "/commit/" + raw_commit.id, " - ", "Commit not found")

#         print("=====================================")
#     # print(f"Mismatch: {count}/{len(missing)}")


def update_comparison_table(dataset):
    # data = load_dataset(dataset)
    pass


def to_latex_table():
    data = load_dataset("results/scalco.csv")
    for e in data:
        print(f"{e[0]} & {e[1][19:]} & {e[5]} \\\\  \hline")  # noqa: W605


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
        if not os.path.exists(
            f"empirical_study/datasets/{filename}/{cve[0]}.json"
        )
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
        generate_report(
            r, a, "json", f"empirical_study/datasets/{filename}/{a.cve_id}"
        )


def run_prospector_and_generate_report(
    vuln_id,
    v_int,
    report_type: str,
    output_file,
    repository_url: str,
    enabled_rules: List[str],
    run_with_llm: bool,
):
    """Call the prospector() and generate_report() functions. This also creates the LLMService singleton
    so that it is available in the context of the job.
    """
    # print(f"Enabled rules: {config.enabled_rules}")  # sanity check
    LLMService(config.llm_service)

    results, advisory_record = prospector(
        vulnerability_id=vuln_id,
        repository_url=repository_url,
        version_interval=v_int,
        backend_address=backend,
        enabled_rules=enabled_rules,
        git_cache=config.git_cache,
        use_llm_repository_url=run_with_llm,
    )

    logger.debug(f"prospector() returned. Generating report now.")

    generate_report(
        results,
        advisory_record,
        report_type,
        output_file,
    )

    # return results, advisory_record
    return f"Ran Prospector on {vuln_id}"


def dispatch_prospector_jobs(filename: str, selected_cves: str):
    """Dispatches jobs to the queue."""

    dataset = load_dataset(INPUT_DATA_PATH + filename + ".csv")
    # dataset = dataset[20:25]

    # Only run a subset of CVEs if the user supplied a selected set
    if len(selected_cves) != 0:
        dataset = [c for c in dataset if c[0] in selected_cves]

    prospector_settings = evaluation_config.prospector_settings
    logger.debug(f"Enabled rules: {prospector_settings.enabled_rules}")

    dispatched_jobs = 0
    for cve in dataset:
        # Skip already existing reports
        if os.path.exists(f"{PROSPECTOR_REPORT_PATH}{filename}/{cve[0]}.json"):
            continue

        dispatched_jobs += 1

        # Send them to Prospector to run
        with Connection(redis.from_url(redis_url)):
            queue = Queue()

            job = Job.create(
                run_prospector_and_generate_report,
                kwargs={
                    "vuln_id": cve[0],
                    "v_int": cve[2],
                    "report_type": "json",
                    "output_file": f"{PROSPECTOR_REPORT_PATH}{filename}/{cve[0]}.json",
                    "repository_url": (
                        cve[1] if prospector_settings.run_with_llm else None
                    ),
                    "enabled_rules": prospector_settings.enabled_rules,
                    "run_with_llm": prospector_settings.run_with_llm,
                },
                description="Prospector Job",
                id=cve[0],
            )

            queue.enqueue_job(job)

        # print(f"Dispatched job {cve[0]} to queue.") # Sanity Check

    print(f"Dispatched {dispatched_jobs} jobs.")


def empty_queue():
    with Connection(redis.from_url(redis_url)):
        queue = Queue("default")

        queue.empty()

        print("Emptied the queue.")
