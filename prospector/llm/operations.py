import sys
from typing import Dict

import validators
from langchain_core.language_models.llms import LLM

from cli.console import ConsoleWriter, MessageStatus
from datamodel.advisory import get_from_mitre
from llm.prompts import best_guess
from log.logger import logger


def get_repository_url(model: LLM, vuln_id: str):
    """Ask an LLM to obtain the repository URL given the advisory description and references.

    Args:
        model (LLM): The instantiated model (instantiated with create_model_instance())
        vuln_id: The ID of the advisory, e.g. CVE-2020-1925.

    Returns:
        The repository URL as a string.

    Raises:
        ValueError if advisory information cannot be obtained or there is an error in the model invocation.
    """
    with ConsoleWriter("Invoking LLM") as console:
        details, _ = get_from_mitre(vuln_id)
        if details is None:
            logger.error("Error when getting advisory information from Mitre.")
            console.print(
                "Error when getting advisory information from Mitre.",
                status=MessageStatus.ERROR,
            )
            sys.exit(1)

        try:
            chain = best_guess | model

            url = chain.invoke(
                {
                    "description": details["descriptions"][0]["value"],
                    "references": details["references"],
                }
            )
            if not validators.url(url):
                logger.error(f"LLM returned invalid URL: {url}")
                console.print(
                    f"LLM returned invalid URL: {url}",
                    status=MessageStatus.ERROR,
                )
                sys.exit(1)
        except Exception as e:
            logger.error(f"Prompt-model chain could not be invoked: {e}")
            console.print(
                "Prompt-model chain could not be invoked.",
                status=MessageStatus.ERROR,
            )
            sys.exit(1)

        return url
