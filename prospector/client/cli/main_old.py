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
from omegaconf import OmegaConf

path_root = os.getcwd()
if path_root not in sys.path:
    sys.path.append(path_root)

# Loading .env file before doint anything else
load_dotenv()

from client.cli.config_parser import load_configuration, parse_cli_args  # noqa: E402
from client.cli.console import ConsoleWriter, MessageStatus  # noqa: E402
from client.cli.prospector_client import DEFAULT_BACKEND  # noqa: E402
from client.cli.prospector_client import TIME_LIMIT_AFTER  # noqa: E402
from client.cli.prospector_client import TIME_LIMIT_BEFORE  # noqa: E402
from client.cli.prospector_client import prospector  # noqa: E402; noqa: E402
from client.cli.report import as_html, as_json, report_on_console  # noqa: E402
from git.git import GIT_CACHE  # noqa: E402

# Load logger before doing anything else
from log.logger import get_level, logger, pretty_log  # noqa: E402
from stats.execution import execution_statistics  # noqa: E402
from util.http import ping_backend  # noqa: E402

# def getConfiguration(customConfigFile=None):
#     # simple is better: only one configuration file is
#     # taken into account, no overriding of options from
#     # one file to the other!

#     # the order is (as soon as one is found, the rest is ignored):
#     # 1) the file passed as argument to this function
#     # 2) ./prospector.conf
#     # 3) ~/.prospector/conf

#     localConfigFile = os.path.join(os.getcwd(), "prospector.conf")
#     userConfigFile = os.path.join(Path.home(), ".prospector/conf")

#     config = configparser.ConfigParser()

#     if customConfigFile and os.path.isfile(customConfigFile):
#         configFile = customConfigFile
#     elif os.path.isfile(localConfigFile):
#         configFile = localConfigFile
#     elif os.path.isfile(userConfigFile):
#         configFile = userConfigFile
#     else:
#         return None

#     logger.info("Loading configuration from " + configFile)
#     config.read(configFile)
#     return parse_config(config)


# def parse_config(configuration: configparser.ConfigParser) -> Dict[str, Any]:
#     """Parse the configuration file and return the options as a dictionary."""
#     options = {}
#     for section in configuration.sections():
#         for option in configuration.options(section):
#             try:
#                 options[option] = configuration.getboolean(section, option)
#             except ValueError:
#                 options[option] = configuration.get(section, option)
#     return options


def main(argv):  # noqa: C901
    with ConsoleWriter("Initialization") as console:
        args = parse_cli_args(argv)

        config = load_configuration(args.get("config"))

        if config is None:
            logger.error("No configuration file found. Cannot proceed.")

            console.print(
                "No configuration file found.",
                status=MessageStatus.ERROR,
            )
            return

        logger.setLevel(args.get("log_level") or config.get("log_level"))
        logger.info(f"Global log level set to {get_level(string=True)}")

        if args.get("cve_id") is None:
            logger.error("No vulnerability id was specified. Cannot proceed.")
            console.print(
                "No vulnerability id was specified. Cannot proceed.",
                status=MessageStatus.ERROR,
            )
            return

        report = args.get("report") or config.get("report")
        report_filename = args.get("report_filename") or config.get("report_filename")

        use_backend = args.get("use_backend") or config.get("use_backend")

        backend = config.get("backend", DEFAULT_BACKEND)

        # if args.get("ping"):
        #     return ping_backend(backend, get_level() < logging.INFO)

        vulnerability_id = args.get("cve_id") or config.get("cve_id")
        repository_url = args.get("repository") or config.get("repository")

        advisory = config.get("advisory")

        description = args.get("description") or advisory.get("description")

        modified_files = args.get("modified_files") or advisory.get("modified_files")
        modified_files = modified_files.split(",")

        advisory_keywords = args.get("keywords") or advisory.get("keywords")
        advisory_keywords = advisory_keywords.split(",")

        filter_extensions = args.get("filter_extensions") or config.get(
            "filter_extensions"
        )
        filter_extensions = filter_extensions.split(",")

        publication_date = args.get("pub_date") or advisory.get("pub_date")
        publication_date = (
            publication_date + "T00:00Z" if publication_date != "" else ""
        )

        # if no backend the filters on the advisory do not work
        use_nvd = args.get("use_nvd") or config.get("use_nvd")

        fetch_references = args.get("fetch_references") or config.get(
            "fetch_references"
        )

        tag_interval = args.get("tag_interval") or config.get("tag_interval")
        version_interval = args.get("version_interval") or config.get(
            "version_interval"
        )
        time_limit_before = TIME_LIMIT_BEFORE
        time_limit_after = TIME_LIMIT_AFTER

        max_candidates = args.get("max_candidates") or config.get("max_candidates")

        git_cache = os.getenv("GIT_CACHE") or config.get("git_cache")

        logger.debug("Using the following configuration:")
        pretty_log(logger, config)

        logger.debug("Vulnerability ID: " + vulnerability_id)
        logger.debug("time-limit before: " + str(time_limit_before))
        logger.debug("time-limit after: " + str(time_limit_after))

        active_rules = ["ALL"]

    results, advisory_record = prospector(
        vulnerability_id=vulnerability_id,
        repository_url=repository_url,
        publication_date=publication_date,
        vuln_descr=description,
        tag_interval=tag_interval,
        filter_extensions=[],
        version_interval=version_interval,
        modified_files=set(modified_files),
        advisory_keywords=set(advisory_keywords),
        time_limit_before=time_limit_before,
        time_limit_after=time_limit_after,
        use_nvd=use_nvd,
        nvd_rest_endpoint="",
        fetch_references=fetch_references,
        backend_address=backend,
        use_backend=use_backend,
        git_cache=git_cache,
        limit_candidates=max_candidates,
        rules=active_rules,
    )

    if args.get("preprocess_only"):
        return

    with ConsoleWriter("Generating report") as console:
        if report == "console":
            report_on_console(results, advisory_record, get_level() < logging.INFO)
        elif report == "json":
            as_json(results, advisory_record, report_filename)
        elif report == "html":
            as_html(results, advisory_record, report_filename)
        elif report == "allfiles":
            as_json(results, advisory_record, report_filename)
            as_html(results, advisory_record, report_filename)
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
        console.print(f"Report saved in {report_filename}")
        return


def signal_handler(signal, frame):
    logger.info("Exited with keyboard interrupt")
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv)
