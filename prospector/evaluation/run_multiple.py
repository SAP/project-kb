# flake8: noqa
import argparse
import os
import signal
import sys

from evaluation.analyse import analyze_prospector, analyze_results_rules
from evaluation.dispatch_jobs import dispatch_prospector_jobs, parallel_execution


def is_missing(path: str):
    return not os.path.exists(path)


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
        dispatch_prospector_jobs(args.input, args.cve)
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
