from llm.llm_service import LLMService  # this is a singleton
from llm.models.openai import OpenAI


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
    def test_sap_gpt4_instantiation(self):
        config = Config("sap", "gpt-4", "0.0")
        llm_service = LLMService(config)
        assert isinstance(llm_service._model, OpenAI)

    # def test_invoke_fail(self):
    #     with pytest.raises(SystemExit):
    #         config = Config("sap", "gpt-35-turbo", "0.0")
    #         model = create_model_instance(config)
    #         vuln_id = "random"
    #         get_repository_url(model=model, vuln_id=vuln_id)
