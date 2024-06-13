import sys
from typing import Dict

import validators
from langchain_core.language_models.llms import LLM

from cli.console import ConsoleWriter, MessageStatus
from llm.model_instantiation import create_model_instance
from llm.prompts import best_guess
from log.logger import logger


class Singleton(object):
    """Singleton class to ensure that any class inheriting from this one can only be instantiated once."""

    def __new__(cls, *args, **kwargs):
        # See if the instance is already in existence, and return it if yes
        if not hasattr(cls, "_singleton_instance"):
            cls._singleton_instance = super(Singleton, cls).__new__(cls)
        return cls._singleton_instance


class LLMService(Singleton):
    def __init__(self, config):
        if hasattr(self, "_instantiated"):
            return
        self._instantiated = True
        self._model: LLM = create_model_instance(config)

    def get_repository_url(self, advisory_description, advisory_references):
        """Ask an LLM to obtain the repository URL given the advisory description and references.

        Args:
            advisory_description (str): The advisory description
            advisory_references (dict): The advisory's references

        Returns:
            The repository URL as a string.

        Raises:
            ValueError if advisory information cannot be obtained or there is an error in the model invocation.
        """
        with ConsoleWriter("Invoking LLM") as console:

            try:
                chain = best_guess | self._model

                url = chain.invoke(
                    {
                        "description": advisory_description,
                        "references": advisory_references,
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
