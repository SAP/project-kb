import validators
from langchain_core.language_models.llms import LLM
from langchain_core.output_parsers import StrOutputParser

from llm.model_instantiation import create_model_instance
from llm.prompts import best_guess
from log.logger import logger
from util.config_parser import LLMServiceConfig
from util.singleton import Singleton


class LLMService(metaclass=Singleton):
    """A wrapper class for all functions requiring an LLM. This class is also a singleton, as only one model
    should be used throughout the program.
    """

    config: LLMServiceConfig = None

    def __init__(self, config: LLMServiceConfig):
        self.config = config
        try:
            self.model: LLM = create_model_instance(
                config.type,
                config.model_name,
                config.ai_core_sk,
                config.temperature,
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
            chain = best_guess | self.model | StrOutputParser()

            url = chain.invoke(
                {
                    "description": advisory_description,
                    "references": advisory_references,
                }
            )
            logger.info(f"LLM returned the following URL: {url}")

            if not validators.url(url):
                raise TypeError(f"LLM returned invalid URL: {url}")

        except Exception as e:
            raise RuntimeError(f"Prompt-model chain could not be invoked: {e}")

        return url
