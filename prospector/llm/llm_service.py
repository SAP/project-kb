import re

import validators
from langchain_core.language_models.llms import LLM
from langchain_core.output_parsers import StrOutputParser

from llm.instantiation import create_model_instance
from llm.prompts import prompt_best_guess
from log.logger import logger
from util.config_parser import LLMServiceConfig
from util.singleton import Singleton


class LLMService(metaclass=Singleton):
    """A wrapper class for all functions requiring an LLM. This class is also a singleton, as only a
    single model should be used throughout the program.
    """

    config: LLMServiceConfig = None

    def __init__(self, config: LLMServiceConfig = None):

        if self.config is None and config is not None:
            self.config = config
        elif self.config is None and config is None:
            raise ValueError(
                "On the first instantiation, a configuration object must be passed."
            )

        try:
            self.model: LLM = create_model_instance(
                self.config.type,
                self.config.model_name,
                self.config.ai_core_sk,
                self.config.temperature,
            )
        except Exception:
            raise

    def get_repository_url(self, advisory_description, advisory_references) -> str:
        """Ask an LLM to obtain the repository URL given the advisory description and references.

        Args:
            advisory_description (str): The advisory description
            advisory_references (dict): The advisory's references

        Returns:
            The repository URL as a string.

        Raises:
            ValueError if advisory information cannot be obtained or there is an error in the model invocation.
        """
        try:
            chain = prompt_best_guess | self.model | StrOutputParser()

            url = chain.invoke(
                {
                    "description": advisory_description,
                    "references": advisory_references,
                }
            )
            logger.info(f"LLM returned the following URL: {url}")

            # delimiters are often returned by the LLM, remove them, if the case
            pattern = r"<output>\s*(https?://[^\s]+)\s*</output>"
            match = re.search(pattern, url)
            if match:
                return match.group(1)

            if not validators.url(url):
                raise TypeError(f"LLM returned invalid URL: {url}")

        except Exception as e:
            raise RuntimeError(f"Prompt-model chain could not be invoked: {e}")

        return url
