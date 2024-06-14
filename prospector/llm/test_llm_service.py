from typing import Any, List

import pytest
from langchain_core.language_models.llms import LLM
from requests_cache import Optional

from llm.llm_service import LLMService  # this is a singleton
from llm.models.gemini import Gemini
from llm.models.mistral import Mistral
from llm.models.openai import OpenAI
from llm.models.sap_llm import SAPLLM
from util.singleton import Singleton


# Mock the llm_service configuration object
class Config:
    type: str = None
    model_name: str = None
    temperature: str = None
    ai_core_sk: str = None

    def __init__(self, type, model_name, temperature, ai_core_sk):
        self.type = type
        self.model_name = model_name
        self.temperature = temperature
        self.ai_core_sk = ai_core_sk


test_vuln_id = "CVE-2024-32480"


# Mock a SAP LLM
class MockLLM(SAPLLM):
    def _call(
        self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any
    ) -> str:
        # Call super() to make sure model_name is valid
        super()._call(prompt, stop, **kwargs)

        url = "https://www.example.com"

        return url


@pytest.fixture(autouse=True)
def reset_singletons():
    # Clean up singleton instances after each test
    Singleton._instances = {}


class TestModel:
    def test_sap_gpt_instantiation(self):
        config = Config("sap", "gpt-4", 0.0, "sk.json")
        llm_service = LLMService(config)
        assert isinstance(llm_service._model, OpenAI)

    def test_sap_gemini_instantiation(self):
        config = Config("sap", "gemini-1.0-pro", 0.0, "sk.json")
        llm_service = LLMService(config)
        assert isinstance(llm_service._model, Gemini)

    def test_sap_mistral_instantiation(self):
        config = Config("sap", "mistralai--mixtral-8x7b-instruct-v01", 0.0, "sk.json")
        llm_service = LLMService(config)
        assert isinstance(llm_service._model, Mistral)

    def test_singleton_instance_creation(self):
        """A second instantiation should return the exisiting instance."""
        config = Config("sap", "gpt-4", 0.0, "sk.json")
        llm_service = LLMService(config)
        same_service = LLMService(config)
        assert (
            llm_service is same_service
        ), "LLMService should return the same instance."

    def test_singleton_same_instance(self):
        """A second instantiation with different parameters should return the existing instance unchanged."""
        config = Config("sap", "gpt-4", 0.0, "sk.json")
        llm_service = LLMService(config)
        config = Config(
            "sap", "gpt-35-turbo", 0.0, "sk.json"
        )  # This instantiation should not work, but instead return the already existing instance
        same_service = LLMService(config)
        assert llm_service is same_service
        assert llm_service._model.model_name == "gpt-4"

    def test_singleton_retains_state(self):
        """Reassigning a field variable of the instance should be allowed and reflected
        across instantiations."""
        config = Config("sap", "gpt-4", 0.0, "sk.json")
        service = LLMService(config)

        service._model = OpenAI(
            model_name="gpt-35-turbo",
            deployment_url="deployment_url_placeholder",
            temperature=0.7,
        )
        same_service = LLMService(config)

        assert same_service._model == OpenAI(
            model_name="gpt-35-turbo",
            deployment_url="deployment_url_placeholder",
            temperature=0.7,
        ), "LLMService should retain state between instantiations"

    def test_get_repository_url(self):
        config = Config("sap", "gpt-4", 0.0, "sk.json")
        service = LLMService(config)
        # Reassign the mock model to the service
        model = MockLLM(
            model_name="gpt-4",
            deployment_url="deployment_url_placeholder",
            temperature=0.7,
            ai_core_sk_file_path="sk.json",
        )
        service._model = model

        assert (
            service.get_repository_url("advisory description", "advisory_references")
            == "https://www.example.com"
        )
