#!/usr/bin/python3
import logging
import os
import signal
import sys
from typing import Any, Dict

from dotenv import load_dotenv

from util.http import ping_backend

path_root = os.getcwd()
if path_root not in sys.path:
    sys.path.append(path_root)


import client.cli.report as report  # noqa: E402
from client.cli.console import ConsoleWriter, MessageStatus  # noqa: E402
from client.cli.prospector_client import TIME_LIMIT_AFTER  # noqa: E402
from client.cli.prospector_client import TIME_LIMIT_BEFORE  # noqa: E402
from client.cli.prospector_client import prospector  # noqa: E402; noqa: E402

# Load logger before doing anything else
from log.logger import get_level, logger, pretty_log  # noqa: E402
from stats.execution import execution_statistics  # noqa: E402
from util.config_parser import get_configuration  # noqa: E402

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

        if config.cve_id is None:
            logger.error("No vulnerability id was specified. Cannot proceed.")
            console.print(
                "No vulnerability id was specified. Cannot proceed.",
                status=MessageStatus.ERROR,
            )
            return

        # if config.ping:
        #     return ping_backend(backend, get_level() < logging.INFO)

        config.pub_date = (
            config.pub_date + "T00:00:00Z" if config.pub_date is not None else ""
        )

        logger.debug("Using the following configuration:")
        pretty_log(logger, config.__dict__)

        logger.debug("Vulnerability ID: " + config.cve_id)

    results, advisory_record = prospector(
        vulnerability_id=config.cve_id,
        repository_url=config.repository,
        publication_date=config.pub_date,
        vuln_descr=config.description,
        # tag_interval=config.tag_interval,
        version_interval=config.version_interval,
        modified_files=config.modified_files,
        advisory_keywords=config.keywords,
        use_nvd=config.use_nvd,
        fetch_references=config.fetch_references,
        backend_address=config.backend,
        use_backend=config.use_backend,
        git_cache=config.git_cache,
        limit_candidates=config.max_candidates,
    )

    if config.preprocess_only:
        return

    report.generate_report(
        results, advisory_record, config.report, config.report_filename
    )

    execution_time = execution_statistics["core"]["execution time"][0]
    ConsoleWriter.print(f"Execution time: {execution_time:.3f}s")

    return


def signal_handler(signal, frame):
    logger.info("Exited with keyboard interrupt")
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv)
