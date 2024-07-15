import itertools
import re

import validators
from langchain_core.language_models.llms import LLM
from langchain_core.output_parsers import StrOutputParser
from requests import HTTPError

from llm.instantiation import create_model_instance
from llm.prompts.classify_commit import zero_shot as cc_zero_shot
from llm.prompts.get_repository_url import prompt_best_guess
from log.logger import logger
from stats.execution import execution_statistics, measure_execution_time
from util.config_parser import LLMServiceConfig
from util.singleton import Singleton

llm_statistics = execution_statistics.sub_collection("LLM")


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

    def get_repository_url(
        self, advisory_description, advisory_references
    ) -> str:
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

            # Shorten the dictionary of references to avoid exceeding the token limit
            if len(advisory_references) >= 300:
                sorted_references = dict(
                    sorted(advisory_references.items(), key=lambda item: item[1])
                )
                advisory_references = dict(
                    itertools.islice(sorted_references.items(), 200)
                )

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

    @measure_execution_time(execution_statistics.sub_collection("LLM"))
    def classify_commit(
        self, diff: str, repository_name: str, commit_message: str
    ) -> bool:
        """Ask an LLM whether a commit is security relevant or not. The response will be either True or False.

        Args:
            candidate (Commit): The commit to input into the LLM

        Returns:
            True if the commit is deemed security relevant, False if not.

        Raises:
            ValueError if there is an error in the model invocation or the response was not valid.
        """
        try:
            chain = cc_zero_shot | self.model | StrOutputParser()

            is_relevant = chain.invoke(
                {
                    "diff": diff,
                    "repository_name": repository_name,
                    "commit_message": commit_message,
                }
            )
            logger.info(f"LLM returned is_relevant={is_relevant}")

        except HTTPError as e:
            # if the diff is too big, a 400 error is returned -> silently ignore by returning False for this commit
            status_code = e.response.status_code
            if status_code == 400:
                return False
            raise RuntimeError(f"Prompt-model chain could not be invoked: {e}")
        except Exception as e:
            raise RuntimeError(f"Prompt-model chain could not be invoked: {e}")

        if "True" in is_relevant:
            return True
        elif "False" in is_relevant:
            return False
        else:
            raise RuntimeError(
                f"The model returned an invalid response: {is_relevant}"
            )
