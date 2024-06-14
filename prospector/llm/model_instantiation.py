from typing import Dict

from dotenv import dotenv_values
from langchain_core.language_models.llms import LLM
from langchain_google_vertexai import ChatVertexAI
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI

from llm.models.gemini import Gemini
from llm.models.mistral import Mistral
from llm.models.openai import OpenAI
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
            - 'temperature' (Optional(float)): The temperature for the model, default 0.0.

    Returns:
        LLM: An instance of the specified LLM model.
    """

    def create_sap_provider(model_name: str, temperature: float):
        model_definition = SAP_MAPPING.get(model_name, None)

        if model_definition is None:
            raise ValueError(f"Model '{model_name}' is not available.")

        model = model_definition._class(
            model_name=model_name,
            deployment_url=model_definition.access_info,
            temperature=temperature,
        )

        return model

    def create_third_party_provider(model_name: str, temperature: float):
        # obtain definition from main mapping
        model_definition = THIRD_PARTY_MAPPING.get(model_name, None)

        if model_definition is None:
            logger.error(f"Model '{model_name}' is not available.")
            raise ValueError(f"Model '{model_name}' is not available.")

        model = model_definition._class(
            model=model_name,
            api_key=model_definition.access_info,
            temperature=temperature,
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
                model = create_sap_provider(
                    llm_config.model_name, llm_config.temperature
                )
            case "third_party":
                model = create_third_party_provider(
                    llm_config.model_name, llm_config.temperature
                )
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
