from datetime import datetime
import json
from typing import Tuple
from evaluation.utils import (
    ANALYSIS_RESULTS_PATH,
    INPUT_DATA_PATH,
    PROSPECTOR_REPORT_PATH,
    load_dataset,
)


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
