from datetime import datetime
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple
from evaluation.utils import (
    ANALYSIS_RESULTS_PATH,
    INPUT_DATA_PATH,
    PROSPECTOR_REPORT_PATH,
    load_dataset,
    load_json_file,
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
            repo_time, avg_cc_time, total_cc_time = _process_llm_statistics(
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
            cc_num_commits = _get_cc_num_commits(filepath)
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


def _process_llm_statistics(filepath: str) -> Tuple[float, float, float]:
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


def _get_cc_num_commits(filepath):
    """Returns how many commits the commit classification rule was applied to."""
    with open(filepath, "r") as file:
        data = json.load(file)

        num = len(
            data["processing_statistics"]["LLM"]["commit_classification"][
                "execution time"
            ]
        )

        return num


def overall_execution_time(input_file: str):
    """Create a boxplot to compare the overall execution time across four
    categories of reports."""
    data = []

    file = f"{INPUT_DATA_PATH}{input_file}.csv"
    dataset = load_dataset(file)
    dataset = dataset[:100]

    directories = {
        "without LLM NVI": "evaluation/data/reports_without_llm",
        "with LLM NVI": "evaluation/data/reports_with_llm",
        "without LLM MVI": "evaluation/data/reports_without_llm_mvi",
        "with LLM MVI": "evaluation/data/reports_with_llm_mvi",
    }

    for batch, path in directories.items():
        for record in dataset:
            try:
                with open(f"{path}/{record[0]}.json", "r") as file:
                    report = json.load(file)
                    core_execution_time = report["processing_statistics"][
                        "core"
                    ]["execution time"][0]
                    data.append(
                        {
                            "set": batch,
                            "core_execution_time": core_execution_time,
                        }
                    )
            except FileNotFoundError:
                continue

    df = pd.DataFrame(data)

    sns.boxplot(x="set", y="core_execution_time", data=df)
    plt.title("Overall Execution Time Comparison")
    plt.xlabel("Report Set")
    plt.ylabel("Execution Time (s)")

    plt.savefig(f"{ANALYSIS_RESULTS_PATH}plots/boxplot-execution-time.png")


def commit_classification_time(input_file: str):
    """Create a boxplot to compare the time used for commit classification
    across both categories of reports with LLM usage."""
    data = []

    file = f"{INPUT_DATA_PATH}{input_file}.csv"
    dataset = load_dataset(file)
    dataset = dataset[:100]

    directories = {
        "NVI": "evaluation/data/reports_with_llm",
        "MVI": "evaluation/data/reports_with_llm_mvi",
    }

    for batch, path in directories.items():
        for record in dataset:
            try:
                report = load_json_file(f"{path}/{record[0]}.json")
                if (
                    "commit_classification"
                    not in report["processing_statistics"]["LLM"]
                ):
                    print(f"No cc stats for {path}/{record[0]}.json")
                    continue
                cc_times = report["processing_statistics"]["LLM"][
                    "commit_classification"
                ]["execution time"]
                data.append(
                    {
                        "set": batch,
                        "core_execution_time": sum(cc_times),
                    }
                )
            except FileNotFoundError:
                continue

    df = pd.DataFrame(data)

    # Create the plot
    plt.figure(figsize=(10, 6))

    # Create boxplot with logarithmic scale
    sns.boxplot(x="set", y="core_execution_time", data=df, showfliers=False)

    # Add individual points
    sns.stripplot(
        x="set",
        y="core_execution_time",
        data=df,
        color=".3",
        size=4,
        jitter=True,
        alpha=0.5,
    )

    # Set logarithmic scale for y-axis
    plt.yscale("log")

    # Customize the plot
    plt.title("Overall Execution Time Comparison (Log Scale)")
    plt.xlabel("Report Set")
    plt.ylabel("Execution Time (s)")

    # Add grid for better readability
    plt.grid(True, which="both", ls="-", alpha=0.2)

    # Tight layout to prevent cutting off labels
    plt.tight_layout()

    # Save the figure
    plt.savefig(
        f"{ANALYSIS_RESULTS_PATH}plots/commit-classification-time.png", dpi=300
    )
    plt.close()


def candidates_execution_time(input_file: str):
    """Creates a plot to see the relationship between number of candidates and
    time needed for the execution."""
    data = {
        "cve_id": [],
        "execution_times": [],
        "num_candidates": [],
    }

    file = f"{INPUT_DATA_PATH}{input_file}.csv"
    dataset = load_dataset(file)
    # dataset = dataset[:100]

    directories = {
        "NVI": "evaluation/data/reports_without_llm_mvi",
        # "MVI": "evaluation/data/reports_with_llm_mvi",
    }

    for batch, path in directories.items():
        for record in dataset:
            try:
                if record[0] == "CVE-2020-8134":
                    continue
                report = load_json_file(f"{path}/{record[0]}.json")
                exec_time = report["processing_statistics"]["core"][
                    "execution time"
                ][0]
                cands = report["processing_statistics"]["core"]["candidates"]

            except Exception as e:
                print(f"Did not process {record[0]} because of {e}")
                continue

            data["cve_id"].append(record[0])
            data["execution_times"].append(exec_time)
            data["num_candidates"].append(cands)

    # Create the plot
    plt.figure(figsize=(10, 6))

    df = pd.DataFrame.from_dict(data)
    print(df)
    sns.jointplot(x="execution_times", y="num_candidates", data=df, kind="reg")

    # Save the figure
    plt.savefig(
        f"{ANALYSIS_RESULTS_PATH}plots/correlation-time-num-candidates.png",
        dpi=300,
    )
    plt.close()

    # Histogram for the number of candidates
    plt.figure(figsize=(10, 6))
    plt.hist(df["num_candidates"], bins=30, edgecolor="black")
    plt.title("Distribution of Number of Candidates")
    plt.xlabel("Number of Candidates")
    plt.ylabel("Frequency")
    plt.savefig(f"{ANALYSIS_RESULTS_PATH}plots/candidates-distribution.png")
    plt.close()
