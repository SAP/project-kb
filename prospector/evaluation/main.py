# flake8: noqa
import argparse
import os
import signal
import sys

from evaluation.analyse import (
    analyse_category_flows,
    analyse_prospector_reports,
    count_existing_reports,
    difference_ground_truth_datasets,
)
from evaluation.analyse_statistics import (
    analyse_statistics,
    candidates_execution_time,
    commit_classification_time,
    overall_execution_time,
)
from evaluation.dispatch_jobs import (
    dispatch_prospector_jobs,
    empty_queue,
)


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
        "-s",
        "--stats",
        action="store_true",
        help="Analyse the statistics field saved in each Prospector report.",
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
        "-eq",
        "--empty-queue",
        help="Empty the Redis Queue",
        action="store_true",
    )

    parser.add_argument(
        "-co",
        "--count",
        help="Count which CVEs from the input data have a corresponding Prospector report.",
        action="store_true",
    )

    parser.add_argument(
        "-fl",
        "--flow",
        help="Analyse which CVEs changed from one category to another given two detailed summary execution JSON files.",
        action="store_true",
    )

    parser.add_argument(
        "-t",
        "--temporary",
        help="Run whichever temporary function is set to temporary. This allows you to write use-once function and run it easily.",
        action="store_true",
    )

    return parser.parse_args()


def main(argv):
    args = parse_cli_args(argv)

    # Run Prospector containerised
    if args.execute and not args.analyze:
        dispatch_prospector_jobs(args.input, args.cve)

    elif args.analyze and not args.execute:
        # analysis of execution statistics in report
        if args.stats:
            # analyse_statistics(args.input)
            # overall_execution_time(args.input)
            # commit_classification_time(args.input)
            candidates_execution_time(args.input)

        elif args.flow:
            analyse_category_flows()
        # analysis of Prospector reports
        else:
            analyse_prospector_reports(args.input)

    # Remove all jobs from the queue
    elif args.empty_queue and not args.execute and not args.stats:
        empty_queue()

    # Count how many reports there are or there are missing
    elif not args.analyze and not args.execute and args.count:
        count_existing_reports(args.input)

    elif not args.analyze and not args.execute and args.temporary:
        difference_ground_truth_datasets()

    # Cannot choose both analyse and execute, stop here.
    elif args.analyze and args.execute:
        sys.exit("Choose either to execute or analyze")


def mute():
    sys.stdout = open(os.devnull, "w")


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
