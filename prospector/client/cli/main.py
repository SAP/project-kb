#!/usr/bin/python3

# from advisory_processor.advisory_processor import AdvisoryProcessor
import argparse
import configparser
import logging
import os
import sys
from pathlib import Path

import requests

import log.config
import log.util
from client.cli.console_report import report_on_console
from client.cli.html_report import report_as_html
from client.cli.json_report import report_as_json
from client.cli.prospector_client import (
    MAX_CANDIDATES,
    TIME_LIMIT_AFTER,
    TIME_LIMIT_BEFORE,
    prospector,
)
from git.git import GIT_CACHE
from simple_hierarchical_storage.execution import ExecutionTimer, execution_statistics

_logger = log.util.init_local_logger()

DEFAULT_BACKEND = "http://localhost:8000"

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
        "-l",
        "--log-level",
        dest="log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
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

    _logger.info("Loading configuration from " + configFile)
    config.read(configFile)
    return config


def ping_backend(server_url: str, verbose: bool = False) -> bool:
    """Tries to contact backend server

    Args:
        server_url (str): the URL of the server endpoint
        verbose (bool, optional): enable verbose output. Defaults to False.
    """

    if verbose:
        _logger.info("Contacting server " + server_url)

    try:
        response = requests.get(server_url)
        if response.status_code != 200:
            _logger.error(
                f"Server replied with an unexpected status: {response.status_code}"
            )
            return False
        else:
            _logger.info("Server ok!")
            return True
    except Exception:
        _logger.error("Server did not reply", exc_info=True)
        return False


def main(argv):  # noqa: C901
    with ExecutionTimer(execution_statistics.sub_collection(name="initialization")):
        args = parseArguments(argv)
        configuration = getConfiguration(args.conf)

        if args.log_level:
            log.config.level = getattr(logging, args.log_level)

        _logger.info(
            f"global log level is set to {logging.getLevelName(log.config.level)}"
        )

        if args.vulnerability_id is None:
            _logger.error("No vulnerability id was specified. Cannot proceed.")
            return False

        if configuration is None:
            _logger.error("Invalid configuration, exiting.")
            return False

        report = configuration["global"].getboolean("report")
        if args.report:
            report = args.report

        if configuration["global"].get("nvd_rest_endpoint"):
            nvd_rest_endpoint = configuration["global"].get("nvd_rest_endpoint")

        backend = configuration["global"].get("backend") or DEFAULT_BACKEND
        if args.backend:
            backend = args.backend

        if args.ping:
            return ping_backend(backend, log.config.level < logging.INFO)

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

        _logger.debug("Using the following configuration:")
        _logger.pretty_log(
            {
                section: dict(configuration[section])
                for section in configuration.sections()
            }
        )

        _logger.debug("Vulnerability ID: " + vulnerability_id)
        _logger.debug("time-limit before: " + str(time_limit_before))
        _logger.debug("time-limit after: " + str(time_limit_after))

    with ExecutionTimer(execution_statistics.sub_collection(name="core")):
        results, advisory_record = prospector(
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
            limit_candidates=max_candidates,
            active_rules=["ALL"],
        )

    with ExecutionTimer(execution_statistics.sub_collection(name="reporting")):
        if report == "console":
            report_on_console(results, advisory_record, log.config.level < logging.INFO)
        elif report == "json":
            report_as_json(results, advisory_record)
        elif report == "html":
            report_as_html(results, advisory_record)
        else:
            _logger.warning("Invalid report type specified, using 'console'")
            report_on_console(results, advisory_record, log.config.level < logging.INFO)

    _logger.info("\n" + execution_statistics.generate_console_tree())
    print(f"WTF = {_logger.level}")
    return True


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv)
