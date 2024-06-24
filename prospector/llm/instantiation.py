import json
from typing import Dict

import requests
from dotenv import dotenv_values
from langchain_core.language_models.llms import LLM
from langchain_google_vertexai import ChatVertexAI
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI

from llm.models.gemini import Gemini
from llm.models.mistral import Mistral
from llm.models.openai import OpenAI

env: Dict[str, str | None] = dotenv_values()


SAP_MAPPING = {
    "gpt-35-turbo": OpenAI,
    "gpt-35-turbo-16k": OpenAI,
    "gpt-35-turbo-0125": OpenAI,
    "gpt-4": OpenAI,
    "gpt-4-32k": OpenAI,
    # "gpt-4-turbo": OpenAI, # currently TBD
    # "gpt-4o": OpenAI,  # currently TBD
    "gemini-1.0-pro": Gemini,
    "mistralai--mixtral-8x7b-instruct-v01": Mistral,
}


THIRD_PARTY_MAPPING = {
    "gpt-4": ChatOpenAI,
    "gpt-3.5-turbo": ChatOpenAI,
    "gemini-pro": ChatVertexAI,
    "mistral-large-latest": ChatMistralAI,
}


def create_model_instance(
    model_type: str,
    model_name: str,
    ai_core_sk_filepath: str,
    temperature: float = 0.0,
) -> LLM:
    """Creates and returns the model object given the user's configuration.

    Args:
        model_type: the way of accessing the LLM API ('sap' for SAP's AI Core, 'third_party' for
                            external providers).
        model_name: which model to use, e.g. gpt-4.
        temperature: the temperature for the model, default 0.0.
        ai_core_sk_filepath: The path to the file containing AI Core credentials

    Returns:
        LLM: An instance of the specified LLM model.

    Raises:
        ValueError: if there is a problem with deploymenturl, model_name or AI Core credentials
    """
    # LASCHA: correct docstring

    def create_sap_provider(
        model_name: str, temperature: float, ai_core_sk_filepath: str
    ):

        deployment_url = env.get("GPT_35_TURBO_URL", None)
        if deployment_url is None:
            raise ValueError(f"Deployment URL for {model_name} is not set.")

        model_class = SAP_MAPPING.get(model_name, None)
        if model_class is None:
            raise ValueError(f"Model '{model_name}' is not available.")

        if ai_core_sk_filepath is None:
            raise ValueError(
                f"AI Core credentials file couldn't be found: '{ai_core_sk_filepath}'"
            )

        model = model_class(
            model_name=model_name,
            deployment_url=deployment_url,
            temperature=temperature,
            ai_core_sk_filepath=ai_core_sk_filepath,
        )

        return model

    def create_third_party_provider(model_name: str, temperature: float):
        model_definition = THIRD_PARTY_MAPPING.get(model_name, None)

        if model_definition is None:
            raise ValueError(f"Model '{model_name}' is not available.")

        model = model_definition._class(
            model=model_name,
            api_key=model_definition.access_info,
            temperature=temperature,
        )

        return model

    # LLM Instantiation
    try:
        match model_type:
            case "sap":
                model = create_sap_provider(
                    model_name,
                    temperature,
                    ai_core_sk_filepath,
                )
            case "third_party":
                model = create_third_party_provider(model_name, temperature)
            case _:
                raise ValueError(
                    f"Invalid LLM type specified (either sap or third_party). '{model_type}' is not available."
                )
    except Exception:
        raise  # re-raise exceptions from create_[sap|third_party]_provider

    return model


def get_headers(ai_core_sk_file_path: str):
    """Generate the request headers to use SAP AI Core. This method generates the authentication token and returns a Dict with headers.

    Returns:
        The headers object needed to send requests to the SAP AI Core.
    """
    with open(ai_core_sk_file_path) as f:
        sk = json.load(f)

    auth_url = f"{sk['url']}/oauth/token"
    client_id = sk["clientid"]
    client_secret = sk["clientsecret"]

    response = requests.post(
        auth_url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=8000,
    )

    headers = {
        "AI-Resource-Group": "default",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {response.json()['access_token']}",
    }
    return headers
