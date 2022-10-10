#!/usr/bin/python3
import logging
import os
import signal
import sys

path_root = os.getcwd()
if path_root not in sys.path:
    sys.path.append(path_root)

import log  # noqa: E402

from client.cli.console import ConsoleWriter, MessageStatus  # noqa: E402
from client.cli.console_report import report_on_console  # noqa: E402
from client.cli.html_report import report_as_html  # noqa: E402
from client.cli.json_report import report_as_json  # noqa: E402
from client.cli.prospector_client import (  # noqa: E402
    MAX_CANDIDATES,  # noqa: E402
    TIME_LIMIT_AFTER,  # noqa: E402
    TIME_LIMIT_BEFORE,  # noqa: E402
    prospector,  # noqa: E402
)
from git.git import GIT_CACHE  # noqa: E402
from stats.execution import execution_statistics  # noqa: E402
from util.http import ping_backend  # noqa: E402

_logger = log.util.init_local_logger()

DEFAULT_BACKEND = "http://localhost:8000"
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
        default="java",
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
        choices=["html", "json", "console"],
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

# Loading .env file before doint anything else
# load_dotenv()

from client.cli.config_parser import get_configuration  # noqa: E402
from client.cli.console import ConsoleWriter, MessageStatus  # noqa: E402
from client.cli.prospector_client import TIME_LIMIT_AFTER  # noqa: E402
from client.cli.prospector_client import TIME_LIMIT_BEFORE  # noqa: E402
from client.cli.prospector_client import prospector  # noqa: E402; noqa: E402
from client.cli.report import as_html, as_json, report_on_console  # noqa: E402

# Load logger before doing anything else
from log.logger import get_level, logger, pretty_log  # noqa: E402
from stats.execution import execution_statistics  # noqa: E402

# from util.http import ping_backend  # noqa: E402


def main(argv):  # noqa: C901
    with ConsoleWriter("Initialization") as console:
        config = get_configuration(argv)

        if not config:
            logger.error("No configuration file found. Cannot proceed.")

            console.print(
                "No configuration file found.",
                status=MessageStatus.ERROR,
            )
            return

        logger.setLevel(config.log_level)
        logger.info(f"Global log level set to {get_level(string=True)}")

        nvd_rest_endpoint = configuration.get("nvd_rest_endpoint", "")  # default ???

        backend = args.backend or configuration.get("backend", DEFAULT_BACKEND)  # ???

        use_backend = args.use_backend

        if args.ping:
            return ping_backend(backend, log.config.level < logging.INFO)

        vulnerability_id = args.vulnerability_id
        repository_url = args.repository
        vuln_descr = args.descr
        filter_extensions = args.filter_extensions.split(",")

        # if args.get("ping"):
        #     return ping_backend(backend, get_level() < logging.INFO)

        config.pub_date = (
            config.pub_date + "T00:00:00Z" if config.pub_date != "" else ""
        )

        time_limit_before = TIME_LIMIT_BEFORE
        time_limit_after = TIME_LIMIT_AFTER

        git_cache = config.git_cache

        logger.debug("Using the following configuration:")
        pretty_log(logger, config.__dict__)

        logger.debug("Vulnerability ID: " + config.cve_id)
        logger.debug(f"time-limit before: {time_limit_before}")
        logger.debug(f"time-limit after: {time_limit_after}")

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
        use_nvd=config.use_nvd,
        nvd_rest_endpoint="",
        fetch_references=config.fetch_references,
        backend_address=config.backend,
        use_backend=config.use_backend,
        git_cache=git_cache,
        limit_candidates=config.max_candidates,
        rules=["ALL"],
    )

    with ConsoleWriter("Generating report") as console:
        report_file = None
        if report == "console":
            report_on_console(results, advisory_record, log.config.level < logging.INFO)
        elif report == "json":
            report_file = report_as_json(
                results, advisory_record, args.report_filename + ".json"
            )
        elif report == "html":
            report_file = report_as_html(
                results, advisory_record, args.report_filename + ".html"
            )
        else:
            _logger.warning("Invalid report type specified, using 'console'")
            console.set_status(MessageStatus.WARNING)
            console.print(
                f"{report} is not a valid report type, 'console' will be used instead",
            )
            report_on_console(results, advisory_record, log.config.level < logging.INFO)

    with ConsoleWriter("Generating report") as console:
        match config.report:
            case "console":
                report_on_console(results, advisory_record, get_level() < logging.INFO)
            case "json":
                as_json(results, advisory_record, config.report_filename)
            case "html":
                as_html(results, advisory_record, config.report_filename)
            case "allfiles":
                as_json(results, advisory_record, config.report_filename)
                as_html(results, advisory_record, config.report_filename)
            case _:
                logger.warning("Invalid report type specified, using 'console'")
                console.set_status(MessageStatus.WARNING)
                console.print(
                    f"{config.report} is not a valid report type, 'console' will be used instead",
                )
                report_on_console(results, advisory_record, get_level() < logging.INFO)

        logger.info("\n" + execution_statistics.generate_console_tree())
        execution_time = execution_statistics["core"]["execution time"][0]
        console.print(f"Execution time: {execution_time:.4f} sec")
        console.print(f"Report saved in {config.report_filename}.{config.report}")
        return


def signal_handler(signal, frame):
    logger.info("Exited with keyboard interrupt")
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv)
