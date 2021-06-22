#!/usr/bin/python3

# from advisory_processor.advisory_processor import AdvisoryProcessor
import argparse
import configparser
import logging
import os
import sys
from pathlib import Path
from pprint import pprint

import jinja2
import requests

from client.cli.prospector_client import (
    MAX_CANDIDATES,
    TIME_LIMIT_AFTER,
    TIME_LIMIT_BEFORE,
    prospector,
)
from datamodel.commit_features import CommitWithFeatures
from git.git import GIT_CACHE

DEFAULT_BACKEND = "http://localhost:8000"

logger = logging.getLogger("prospector")

# VERSION = '0.1.0'
# SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
# print(SCRIPT_PATH)


def parseArguments(args):
    parser = argparse.ArgumentParser(description="Prospector CLI")
    parser.add_argument(
        "vulnerability_id", nargs="?", help="ID of the vulnerability to analyze"
    )

    parser.add_argument("--repository", default="", help="Git repository")

    parser.add_argument(
        "--pub-date", default="", help="Publication date of the advisory"
    )

    parser.add_argument("--descr", default="", help="Text of the advisory")

    parser.add_argument(
        "--max-candidates",
        default=MAX_CANDIDATES,
        type=int,
        help="Maximum number of candidates to consider",
    )

    parser.add_argument(
        "--tag-interval",
        default="",
        type=str,
        help="Tag interval (X,Y) to consider (the commit must be reachable from Y but not from X, and must not be older than X)",
    )

    parser.add_argument(
        "--version-interval",
        default="",
        type=str,
        help="Version interval (X,Y) to consider (the corresponding tags will be inferred automatically, and the commit must be reachable from Y but not from X, and must not be older than X)",
    )

    parser.add_argument(
        "--modified-files",
        default="",
        type=str,
        help="Files (partial names are ok, comma separated) that the candidate commits are supposed to touch",
    )

    parser.add_argument("--use-nvd", action="store_true", help="Get data from NVD")

    parser.add_argument(
        "--backend", default=DEFAULT_BACKEND, help="URL of the backend server"
    )

    parser.add_argument(
        "--report",
        default="console",
        help="how to show the results (options: console, json, html)",
    )

    parser.add_argument("-c", "--conf", help="specify configuration file")

    parser.add_argument(
        "-p", "--ping", help="Contact server to check it's alive", action="store_true"
    )

    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )

    parser.add_argument(
        "-d",
        "--debug",
        help="increase output verbosity even more and output stack-traces on exceptions",
        action="store_true",
    )

    return parser.parse_args(args[1:])


def getConfiguration(customConfigFile=None):
    # simple is better: only one configuration file is
    # taken into account, no overriding of options from
    # one file to the other!

    # the order is (as soon as one is found, the rest is ignored):
    # 1) the file passed as argument to this function
    # 2) ./prospector.conf
    # 3) ~/.prospector/conf

    localConfigFile = os.path.join(os.getcwd(), "prospector.conf")
    userConfigFile = os.path.join(Path.home(), ".prospector/conf")

    config = configparser.ConfigParser()

    if customConfigFile and os.path.isfile(customConfigFile):
        configFile = customConfigFile
    elif os.path.isfile(localConfigFile):
        configFile = localConfigFile
    elif os.path.isfile(userConfigFile):
        configFile = userConfigFile
    else:
        return None

    print("Loading configuration from " + configFile)
    config.read(configFile)
    return config


def ping_backend(server_url: str, verbose: bool = False) -> bool:
    """Tries to contact backend server

    Args:
        server_url (str): the URL of the server endpoint
        verbose (bool, optional): enable verbose output. Defaults to False.
    """

    if verbose:
        print("Contacting server " + server_url)

    try:
        response = requests.get(server_url)
        if response.status_code != 200:
            print("Server replied with an unexpected status: " + response.status_code)
            return False
        else:
            print("Server ok!")
            return True
    except Exception:
        print("Server did not reply")
        return False


def make_report_json(results: "list[CommitWithFeatures]"):
    filename = "prospector-report.json"
    print("Writing results to " + filename)


def make_report_html(results: "list[CommitWithFeatures]"):
    filename = "prospector-report.html"
    print("Writing results to " + filename)
    environment = jinja2.Environment(
        loader=jinja2.PackageLoader(__name__), autoescape=jinja2.select_autoescape()
    )
    template = environment.get_template("results.html")
    print(template.render())


def make_report_console(results: "list[CommitWithFeatures]", verbose=False):
    def format_annotations(commit: CommitWithFeatures) -> str:
        out = ""
        if verbose:
            for tag in commit.annotations:
                out += " - [{}] {}".format(tag, commit.annotations[tag])
        else:
            out = ",".join(commit.annotations.keys())

        return out

    print("-" * 80)
    print("Rule filtered results")
    print("-" * 80)
    count = 0
    for commit in results:
        count += 1
        print(
            "\n----------\n{}/commit/{}\n".format(
                commit.commit.repository, commit.commit.commit_id
            )
        )
        print(commit.commit.changed_files)
        print(commit.commit.message + "\n")
        print(format_annotations(commit))

    print("-----")
    print("Found {} candidates".format(count))


def main(argv):  # noqa: C901
    args = parseArguments(argv)
    configuration = getConfiguration(args.conf)

    if args.vulnerability_id is None:
        print("No vulnerability id was specified. Cannot proceed.")
        return False

    if configuration is None:
        print("Invalid configuration, exiting.")
        return False

    debug = configuration["global"].getboolean("debug")
    if args.debug:
        debug = args.debug

    verbose = configuration["global"].getboolean("verbose")
    if args.verbose:
        verbose = args.verbose

    report = configuration["global"].getboolean("report")
    if args.report:
        report = args.report

    if debug:
        verbose = True

    if configuration["global"].get("nvd_rest_endpoint"):
        nvd_rest_endpoint = configuration["global"].get("nvd_rest_endpoint")

    backend = configuration["global"].get("backend") or DEFAULT_BACKEND
    if args.backend:
        backend = args.backend

    if args.ping:
        return ping_backend(backend, verbose)

    vulnerability_id = args.vulnerability_id
    repository_url = args.repository

    vuln_descr = args.descr
    use_nvd = args.use_nvd
    tag_interval = args.tag_interval
    version_interval = args.version_interval
    time_limit_before = TIME_LIMIT_BEFORE
    time_limit_after = TIME_LIMIT_AFTER
    max_candidates = args.max_candidates
    modified_files = args.modified_files.split(",")

    publication_date = ""
    if args.pub_date != "":
        publication_date = args.pub_date + "T00:00Z"
        # if the date is forced manually, the time interval can
        # be restricted
        # time_limit_before = int(time_limit_before / 5)
        # time_limit_after = int(time_limit_after / 2)

    git_cache = GIT_CACHE
    if os.environ["GIT_CACHE"]:
        git_cache = os.environ["GIT_CACHE"]
    if configuration["global"].get("git_cache"):
        git_cache = configuration["global"].get("git_cache")

    if verbose:
        print("Using the following configuration:")
        pprint(
            {
                section: dict(configuration[section])
                for section in configuration.sections()
            }
        )

    if verbose:
        print("Vulnerability ID: " + vulnerability_id)
        print("time-limit before: " + str(time_limit_before))
        print("time-limit after: " + str(time_limit_after))

    results = prospector(
        vulnerability_id=vulnerability_id,
        repository_url=repository_url,
        publication_date=publication_date,
        vuln_descr=vuln_descr,
        tag_interval=tag_interval,
        version_interval=version_interval,
        modified_files=modified_files,
        time_limit_before=time_limit_before,
        time_limit_after=time_limit_after,
        use_nvd=use_nvd,
        nvd_rest_endpoint=nvd_rest_endpoint,
        backend_address=backend,
        git_cache=git_cache,
        verbose=verbose,
        debug=debug,
        limit_candidates=max_candidates,
    )

    if report == "console":
        make_report_console(results, verbose=verbose)
    elif report == "json":
        make_report_json(results)
    elif report == "html":
        make_report_html(results)
    else:
        print("Invalid report type specified, using 'console'")
        make_report_console(results, verbose=verbose)
    return True


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)
