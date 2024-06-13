import pytest
import requests
from langchain_openai import ChatOpenAI

from llm.llm_service import create_model_instance, get_repository_url
from llm.models import Gemini, Mistral, OpenAI


# Mock the llm_service configuration object
class Config:
    type: str = None
    model_name: str = None
    temperature: str = None

    def __init__(self, type, model_name, temperature):
        self.type = type
        self.model_name = model_name
        self.temperature = temperature


# Vulnerability ID
vuln_id = "CVE-2024-32480"


class TestModel:
    def test_sap_gpt35_instantiation(self):
        config = Config("sap", "gpt-35-turbo", "0.0")
        model = create_model_instance(config)
        assert isinstance(model, OpenAI)

    def test_sap_gpt4_instantiation(self):
        config = Config("sap", "gpt-4", "0.0")
        model = create_model_instance(config)
        assert isinstance(model, OpenAI)

    def test_thirdparty_gpt35_instantiation(self):
        config = Config("third_party", "gpt-3.5-turbo", "0.0")
        model = create_model_instance(config)
        assert isinstance(model, ChatOpenAI)

    def test_thirdparty_gpt4_instantiation(self):
        config = Config("third_party", "gpt-4", "0.0")
        model = create_model_instance(config)
        assert isinstance(model, ChatOpenAI)

    def test_invoke_fail(self):
        with pytest.raises(SystemExit):
            config = Config("sap", "gpt-35-turbo", "0.0")
            model = create_model_instance(config)
            vuln_id = "random"
            get_repository_url(model=model, vuln_id=vuln_id)
