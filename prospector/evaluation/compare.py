# Compare a list of Prospector JSON reports to their counterparts
# - to find out which reports have changed since D63 and what the difference is
from datetime import datetime
import json
import os
from evaluation.utils import (
    ANALYSIS_RESULTS_PATH,
    logger,
    config,
    load_json_file,
)


def is_same_report(report1, report2) -> bool:
    json1 = load_json_file(report1)
    json2 = load_json_file(report2)
    return json1 == json2


def has_candidates(path: str) -> bool:
    report = load_json_file(path)
    return len(report["commits"]) > 0


def is_first_candidate_same(path1: str, path2: str) -> bool:
    report1 = load_json_file(path1)
    report2 = load_json_file(path2)

    if not has_candidates(path1) and has_candidates(path2):
        return True

    if not has_candidates(path1) or not has_candidates(path2):
        return False

    id1 = report1["commits"][0]["commit_id"]
    id2 = report2["commits"][0]["commit_id"]

    same = id1 == id2

    if not same and report1["commits"][0]["twins"]:
        # Check if they are twins
        twins_report1 = [twin[1] for twin in report1["commits"][0]["twins"]]
        if id2 in twins_report1:
            same = True

    return same


def references_are_same(path1: str, path2: str) -> bool:
    report1 = load_json_file(path1)
    report2 = load_json_file(path2)

    return (
        report1["advisory_record"]["references"]
        == report2["advisory_record"]["references"]
    )


def candidate_in_both(path1: str, path2: str) -> bool:
    report1 = load_json_file(path1)
    report2 = load_json_file(path2)

    report2_candidates = [commit["commit_id"] for commit in report2["commits"]]
    if report1["commits"][0]["commit_id"] in report2_candidates:
        return True

    return False


def tags_are_same(path1: str, path2: str) -> bool:
    report1 = load_json_file(path1)
    report2 = load_json_file(path2)

    id_first_candidate1 = report1["commits"][0]["commit_id"]
    tags_first_candidate1 = report1["commits"][0]["tags"]

    for commit in report2["commits"]:
        if commit["commit_id"] == id_first_candidate1:
            return tags_first_candidate1 == commit["tags"]

    return False


def main():
    directory1 = config.compare_directory1
    directory2 = config.compare_directory2

    logger.info(f"Comparing reports in {directory1} and {directory2}.")

    ## Things to measure
    counterpart_exists = []
    missing_in_directory1 = []
    missing_in_directory2 = []

    entirely_same = []
    same_references = []
    same_first_candidate = []
    different_first_candidate = []
    has_no_candidates = []

    # Different first candidate
    dfc_references = []
    dfc_first_candidate_not_in_counterpart = []
    dfc_not_in_counterpart_despite_same_references = []
    dfc_not_in_counterpart_despite_same_tags = []
    dfc_tags_and_refs = []
    dfc_only_tags = []

    # Get reports from first directory
    reports1 = [f for f in os.listdir(directory1)]
    # get reports from second directory
    reports2 = [f for f in os.listdir(directory2)]

    for report in reports1:
        if report not in reports2:
            missing_in_directory2.append(report)
            continue

        counterpart_exists.append(report)
        reports2.remove(report)

        if is_same_report(directory1 + report, directory2 + report):
            entirely_same.append(report)
            same_references.append(report)
            same_first_candidate.append(report)
            continue

        if is_first_candidate_same(directory1 + report, directory2 + report):
            same_first_candidate.append(report)
            continue

        # Reports have different first candidates
        different_first_candidate.append(report)

        # because of different references
        if not references_are_same(directory1 + report, directory2 + report):
            dfc_references.append(report)

        # because one of the reports has no ranked candidates
        if not has_candidates(directory1 + report):
            has_no_candidates.append((report, "directory 1"))
            continue
        elif not has_candidates(directory2 + report):
            has_no_candidates.append((report, "directory 2"))
            continue

        if not candidate_in_both(directory1 + report, directory2 + report):
            dfc_first_candidate_not_in_counterpart.append(report)
            if report not in dfc_references:
                dfc_not_in_counterpart_despite_same_references.append(report)
            elif report not in (dfc_tags_and_refs + dfc_only_tags):
                dfc_not_in_counterpart_despite_same_tags.append(report)
            continue

        # because of different tags
        if not tags_are_same(directory1 + report, directory2 + report):
            if report in dfc_references:
                dfc_tags_and_refs.append(report)
            else:
                dfc_only_tags.append(report)
            continue

        print(report)

    missing_in_directory1 = reports2

    # Prepare results
    results = {
        "timestamp": datetime.now().strftime("%d-%m-%Y, %H:%M"),
        "directory1": directory1,
        "directory2": directory2,
        "counterparts_exist": len(counterpart_exists),
        "missing_in_directory1": len(missing_in_directory1),
        "missing_in_directory2": len(missing_in_directory2),
        "reports_comparison": {
            "entirely_same": len(entirely_same),
            "same_first_candidate": {
                "count": len(same_first_candidate),
            },
            "different_first_candidate": {
                "count": len(different_first_candidate),
                "reports": different_first_candidate,
                "of_which_have_different_references": {
                    "count": len(dfc_references),
                    "reports": dfc_references,
                },
                "of_which_have_different_tags": {
                    "count": len(dfc_only_tags),
                    "reports": dfc_only_tags,
                },
                "one_report_has_no_candidates_at_all": {
                    "count": len(has_no_candidates),
                    "reports": has_no_candidates,
                },
                "first_candidate_not_in_counterpart": {
                    "count": len(dfc_first_candidate_not_in_counterpart),
                    "reports": dfc_first_candidate_not_in_counterpart,
                    "of_which_have_same_references": {
                        "count": len(
                            dfc_not_in_counterpart_despite_same_references
                        ),
                        "reports": dfc_not_in_counterpart_despite_same_references,
                    },
                    "of_which_have_same_tags": {
                        "count": len(
                            dfc_not_in_counterpart_despite_same_tags,
                        ),
                        "reports": dfc_not_in_counterpart_despite_same_tags,
                    },
                },
            },
        },
    }

    # Append results to JSON file
    output_path = os.path.join(ANALYSIS_RESULTS_PATH, "reports_comparison.json")

    try:
        with open(output_path, "r") as f:
            existing_data = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {"reports_comparison": []}

    # Append new result
    existing_data["reports_comparison"].append(results)

    # Write results to JSON file
    output_path = os.path.join(ANALYSIS_RESULTS_PATH, "reports_comparison.json")
    with open(output_path, "w") as f:
        json.dump(existing_data, f, indent=2)

    logger.info(f"Comparison results written to {output_path}")


if __name__ == "__main__":
    main()
