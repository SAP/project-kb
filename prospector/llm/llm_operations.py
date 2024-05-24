import sys
from typing import Dict

import validators
from dotenv import dotenv_values
from langchain_core.language_models.llms import LLM
from langchain_google_vertexai import ChatVertexAI
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI

from cli.console import ConsoleWriter, MessageStatus
from datamodel.advisory import get_from_mitre
from llm.models import Gemini, Mistral, OpenAI
from llm.prompts import best_guess
from log.logger import logger


class ModelDef:
    def __init__(self, access_info: str, _class: LLM):
        self.access_info = (
            access_info  # either deployment_url (for SAP) or API key (for Third Party)
        )
        self._class = _class


env: Dict[str, str | None] = dotenv_values()

SAP_MAPPING = {
    "gpt-35-turbo": ModelDef(env.get("GPT_35_TURBO_URL", None), OpenAI),
    "gpt-35-turbo-16k": ModelDef(env.get("GPT_35_TURBO_16K_URL", None), OpenAI),
    "gpt-35-turbo-0125": ModelDef(env.get("GPT_35_TURBO_0125_URL", None), OpenAI),
    "gpt-4": ModelDef(env.get("GPT_4_URL", None), OpenAI),
    "gpt-4-32k": ModelDef(env.get("GPT_4_32K_URL", None), OpenAI),
    # "gpt-4-turbo": env.get("GPT_4_TURBO_URL", None), # currently TBD: https://github.tools.sap/I343697/generative-ai-hub-readme
    # "gpt-4o": env.get("GPT_4O_URL", None),  # currently TBD: https://github.tools.sap/I343697/generative-ai-hub-readme
    "gemini-1.0-pro": ModelDef(env.get("GEMINI_1_0_PRO_URL", None), Gemini),
    "mistralai--mixtral-8x7b-instruct-v01": ModelDef(
        env.get("MISTRALAI_MIXTRAL_8X7B_INSTRUCT_V01", None), Mistral
    ),
}

THIRD_PARTY_MAPPING = {
    "gpt-4": ModelDef(env.get("OPENAI_API_KEY", None), ChatOpenAI),
    "gpt-3.5-turbo": ModelDef(env.get("OPENAI_API_KEY", None), ChatOpenAI),
    "gemini-pro": ModelDef(env.get("GOOGLE_API_KEY", None), ChatVertexAI),
    "mistral-large-latest": ModelDef(env.get("MISTRAL_API_KEY", None), ChatMistralAI),
}


def create_model_instance(llm_config) -> LLM:
    """Creates and returns the model object given the user's configuration.

    Args:
        llm_config (dict): A dictionary containing the configuration for the LLM. Expected keys are:
            - 'type' (str): Method for accessing the LLM API ('sap' for SAP's AI Core, 'third_party' for
                            external providers).
            - 'model_name' (str): Which model to use, e.g. gpt-4.

    Returns:
        LLM: An instance of the specified LLM model.
    """

    def create_sap_provider(model_name: str):
        d = SAP_MAPPING.get(model_name, None)

        if d is None:
            raise ValueError(f"Model '{model_name}' is not available.")

        model = d._class(
            model_name=model_name,
            deployment_url=d.access_info,
        )

        return model

    def create_third_party_provider(model_name: str):
        # obtain definition from main mapping
        d = THIRD_PARTY_MAPPING.get(model_name, None)

        if d is None:
            logger.error(f"Model '{model_name}' is not available.")
            raise ValueError(f"Model '{model_name}' is not available.")

        model = d._class(
            model=model_name,
            api_key=d.access_info,
        )

        return model

    if llm_config is None:
        raise ValueError(
            "When using LLM support, please add necessary parameters to configuration file."
        )

    # LLM Instantiation
    try:
        match llm_config.type:
            case "sap":
                model = create_sap_provider(llm_config.model_name)
            case "third_party":
                model = create_third_party_provider(llm_config.model_name)
            case _:
                logger.error(
                    f"Invalid LLM type specified, '{llm_config.type}' is not available."
                )
                raise ValueError(
                    f"Invalid LLM type specified, '{llm_config.type}' is not available."
                )
    except Exception as e:
        logger.error(f"Problem when initialising model: {e}")
        raise ValueError(f"Problem when initialising model: {e}")

    return model


def get_repository_url(llm_config: Dict, vuln_id: str):
    """Ask an LLM to obtain the repository URL given the advisory description and references.

    Args:
        llm_config (dict): A dictionary containing the configuration for the LLM. Expected keys are:
            - 'type' (str): Method for accessing the LLM API ('sap' for SAP's AI Core, 'third_party' for
                            external providers).
            - 'model_name' (str): Which model to use, e.g. gpt-4.
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
            model = create_model_instance(llm_config=llm_config)
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
