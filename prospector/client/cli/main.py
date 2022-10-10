#!/usr/bin/python3
import argparse
import configparser
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv


path_root = os.getcwd()
if path_root not in sys.path:
    sys.path.append(path_root)

# Loading .env file before doint anything else
load_dotenv()

# Load logger before doing anything else
from log.logger import logger, get_level, pretty_log  # noqa: E402

from client.cli.console import ConsoleWriter, MessageStatus  # noqa: E402
from client.cli.report import as_json, as_html, report_on_console  # noqa: E402
from client.cli.prospector_client import (  # noqa: E402
    MAX_CANDIDATES,  # noqa: E402
    TIME_LIMIT_AFTER,  # noqa: E402
    TIME_LIMIT_BEFORE,  # noqa: E402
    DEFAULT_BACKEND,  # noqa: E402
    prospector,  # noqa: E402
)
from git.git import GIT_CACHE  # noqa: E402
from stats.execution import execution_statistics  # noqa: E402
from util.http import ping_backend  # noqa: E402


# VERSION = '0.1.0'
# SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
# print(SCRIPT_PATH)


def parseArguments(args):
    parser = argparse.ArgumentParser(description="Prospector CLI")
    parser.add_argument(
        "vulnerability_id",
        nargs="?",
        type=str,
        help="ID of the vulnerability to analyze",
    )

    parser.add_argument("--repository", default="", type=str, help="Git repository")

    parser.add_argument(
        "--find-twin",
        default="",
        type=str,
        help="Lookup for a twin of the specified commit",
    )

    parser.add_argument(
        "--preprocess-only",
        action="store_true",
        help="Only preprocess the commits for the specified repository",
    )

    parser.add_argument(
        "--pub-date", default="", help="Publication date of the advisory"
    )

    parser.add_argument("--descr", default="", type=str, help="Text of the advisory")

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

    parser.add_argument(
        "--filter-extensions",
        default="",
        type=str,
        help="Filter out commits that do not modify at least one file with this extension",
    )

    parser.add_argument(
        "--advisory-keywords",
        default=None,
        type=str,
        help="Add the specified keywords to the advisory record",
    )

    parser.add_argument(
        "--use-nvd", default=None, action="store_true", help="Get data from NVD"
    )

    # FIXME: with python 3.9 we can use the new built-in capabilities of argparse to get rid of this
    parser.add_argument(
        "--no-use-nvd", default=None, action="store_true", help="Get data from NVD"
    )

    parser.add_argument(
        "--fetch-references",
        default=True,
        action="store_true",
        help="Fetch content of references linked from the advisory",
    )

    parser.add_argument(
        "--backend", default=DEFAULT_BACKEND, type=str, help="URL of the backend server"
    )

    parser.add_argument(
        "--use-backend",
        default="always",
        choices=["always", "never", "optional"],
        type=str,
        help="Use the backend server",
    )

    parser.add_argument(
        "--report",
        default="html",
        choices=["html", "json", "console", "allfiles"],
        type=str,
        help="Format of the report (options: console, json, html)",
    )

    parser.add_argument(
        "--report-filename",
        default="prospector-report",
        type=str,
        help="File where to save the report",
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

    return parser.parse_args()


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

    logger.info("Loading configuration from " + configFile)
    config.read(configFile)
    return parse_config(config)


def parse_config(configuration: configparser.ConfigParser) -> Dict[str, Any]:
    """Parse the configuration file and return the options as a dictionary."""
    options = {}
    for section in configuration.sections():
        for option in configuration.options(section):
            try:
                options[option] = configuration.getboolean(section, option)
            except ValueError:
                options[option] = configuration.get(section, option)
    return options


def main(argv):  # noqa: C901
    with ConsoleWriter("Initialization") as console:
        args = parseArguments(argv)

        if args.log_level:
            logger.setLevel(args.log_level)

        logger.info(f"global log level is set to {get_level(string=True)}")

        if args.vulnerability_id is None:
            logger.error("No vulnerability id was specified. Cannot proceed.")
            console.print(
                "No vulnerability id was specified. Cannot proceed.",
                status=MessageStatus.ERROR,
            )
            return False

        configuration = getConfiguration(args.conf)

        if configuration is None:
            logger.error("Invalid configuration, exiting.")
            return False

        report = args.report or configuration.get("report")
        report_filename = args.report_filename or configuration.get("report_filename")

        nvd_rest_endpoint = configuration.get("nvd_rest_endpoint", "")  # default ???

        backend = args.backend or configuration.get("backend", DEFAULT_BACKEND)  # ???

        use_backend = args.use_backend

        if args.ping:
            return ping_backend(backend, get_level() < logging.INFO)

        vulnerability_id = args.vulnerability_id
        repository_url = args.repository
        vuln_descr = args.descr
        filter_extensions = args.filter_extensions.split(",")

        # if no backend the filters on the advisory do not work
        use_nvd = False
        if args.vulnerability_id.casefold().startswith("cve-"):
            use_nvd = True
        if args.use_nvd is True:
            use_nvd = True
        elif args.no_use_nvd is True:
            use_nvd = False

        fetch_references = args.fetch_references or configuration.get(
            "fetch_references", False
        )

        tag_interval = args.tag_interval
        version_interval = args.version_interval
        time_limit_before = TIME_LIMIT_BEFORE
        time_limit_after = TIME_LIMIT_AFTER
        max_candidates = args.max_candidates
        modified_files = args.modified_files.split(",") if args.modified_files else []
        advisory_keywords = (
            args.advisory_keywords.split(",") if args.advisory_keywords else []
        )

        publication_date = ""
        if args.pub_date != "":
            publication_date = args.pub_date + "T00:00Z"
        # if the date is forced manually, the time interval can
        # be restricted
        # time_limit_before = int(time_limit_before / 5)
        # time_limit_after = int(time_limit_after / 2)

        git_cache = os.getenv("GIT_CACHE", default=GIT_CACHE)

        git_cache = configuration.get("git_cache", git_cache)

        logger.debug("Using the following configuration:")
        pretty_log(logger, configuration)

        logger.debug("Vulnerability ID: " + vulnerability_id)
        logger.debug("time-limit before: " + str(time_limit_before))
        logger.debug("time-limit after: " + str(time_limit_after))

        active_rules = ["ALL"]

    results, advisory_record = prospector(
        vulnerability_id=vulnerability_id,
        repository_url=repository_url,
        publication_date=publication_date,
        vuln_descr=vuln_descr,
        tag_interval=tag_interval,
        filter_extensions=filter_extensions,
        version_interval=version_interval,
        modified_files=set(modified_files),
        advisory_keywords=set(advisory_keywords),
        time_limit_before=time_limit_before,
        time_limit_after=time_limit_after,
        use_nvd=use_nvd,
        nvd_rest_endpoint=nvd_rest_endpoint,
        fetch_references=fetch_references,
        backend_address=backend,
        use_backend=use_backend,
        git_cache=git_cache,
        limit_candidates=max_candidates,
        rules=active_rules,
    )

    if args.preprocess_only:
        return True

    with ConsoleWriter("Generating report") as console:
        report_file = None
        if report == "console":
            report_on_console(results, advisory_record, get_level() < logging.INFO)
        elif report == "json":
            report_file = report_as_json(
                results, advisory_record, args.report_filename + ".json"
            )
        elif report == "html":
            report_file = report_as_html(
                results, advisory_record, args.report_filename + ".html"
            )
        else:
            logger.warning("Invalid report type specified, using 'console'")
            console.set_status(MessageStatus.WARNING)
            console.print(
                f"{report} is not a valid report type, 'console' will be used instead",
            )
            report_on_console(results, advisory_record, get_level() < logging.INFO)

        logger.info("\n" + execution_statistics.generate_console_tree())
        execution_time = execution_statistics["core"]["execution time"][0]
        console.print(f"Execution time: {execution_time:.4f} sec")
        if report_file:
            console.print(f"Report saved in {report_file}")
        return True


def signal_handler(signal, frame):
    logger.info("Exited with keyboard interrupt")
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv)
