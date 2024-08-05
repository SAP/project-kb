#!/usr/bin/python3
import os
import signal
import sys

from llm.llm_service import LLMService
from util.http import ping_backend

path_root = os.getcwd()
if path_root not in sys.path:
    sys.path.append(path_root)


import core.report as report  # noqa: E402
from cli.console import ConsoleWriter, MessageStatus  # noqa: E402
from core.prospector import prospector  # noqa: E402; noqa: E402

# Load logger before doing anything else
from log.logger import get_level, logger, pretty_log  # noqa: E402
from stats.execution import execution_statistics  # noqa: E402
from util.config_parser import get_configuration  # noqa: E402

# from util.http import ping_backend  # noqa: E402


def main(argv):  # noqa: C901
    with ConsoleWriter("Initialization") as console:
        config = get_configuration(argv)
        if not config:
            logger.error(
                "No configuration file found, or error in configuration file. Cannot proceed."
            )

            console.print(
                "No configuration file found, or error in configuration file. Check logs.",
                status=MessageStatus.ERROR,
            )
            return

        logger.setLevel(config.log_level)
        logger.info(f"Global log level set to {get_level(string=True)}")

        if config.vuln_id is None:
            logger.error("No vulnerability id was specified. Cannot proceed.")
            console.print(
                "No configuration file found.",
                status=MessageStatus.ERROR,
            )
            return

        # if config.ping:
        #     return ping_backend(backend, get_level() < logging.INFO)

        # Whether to use the LLMService
        if config.llm_service:
            if (
                not config.repository
                and not config.llm_service.use_llm_repository_url
            ):
                logger.error(
                    "Repository URL was neither specified nor allowed to obtain with LLM support. One must be set."
                )
                console.print(
                    "Please set the `--repository` parameter or enable LLM support to infer the repository URL.",
                    status=MessageStatus.ERROR,
                )
                return

            # Create the LLMService Singleton for later use
            try:
                LLMService(config.llm_service)
            except Exception as e:
                logger.error(f"Problem with LLMService instantiation: {e}")
                console.print(
                    "LLMService could not be created. Check logs.",
                    status=MessageStatus.ERROR,
                )
                return

        config.pub_date = (
            config.pub_date + "T00:00:00Z"
            if config.pub_date is not None
            else ""
        )

        logger.debug("Using the following configuration:")
        pretty_log(logger, config.__dict__)

        logger.debug("Vulnerability ID: " + config.vuln_id)

    params = {
        "vulnerability_id": config.vuln_id,
        "repository_url": config.repository,
        "publication_date": config.pub_date,
        "vuln_descr": config.description,
        "version_interval": config.version_interval,
        "modified_files": config.modified_files,
        "advisory_keywords": config.keywords,
        "use_nvd": config.use_nvd,
        # fetch_references=config.fetch_references,
        "backend_address": config.backend,
        "use_backend": config.use_backend,
        "git_cache": config.git_cache,
        "limit_candidates": config.max_candidates,
        # ignore_adv_refs=config.ignore_refs,
        "use_llm_repository_url": config.llm_service.use_llm_repository_url,
        "enabled_rules": config.enabled_rules,
    }

    try:
        results, advisory_record = prospector(**params)
    except Exception as e:
        ConsoleWriter.print(
            f"Prospector function couldn't return successfully with {config.vuln_id}: {e}\n"
        )
        return

    if config.preprocess_only:
        return

    report.generate_report(
        results,
        advisory_record,
        config.report,
        config.report_filename,
        params,
        config.report_diff,
    )

    execution_time = execution_statistics["core"]["execution time"][0]
    ConsoleWriter.print(f"Execution time: {execution_time:.3f}s\n")

    return


def signal_handler(signal, frame):
    logger.info("Exited with keyboard interrupt")
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv)
