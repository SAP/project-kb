from typing import Any, Dict, List, Optional

import requests
from langchain_core.language_models.llms import LLM

import llm.model_instantiation as instantiation
from log.logger import logger


class OpenAI(LLM):
    model_name: str
    deployment_url: str
    temperature: float
    ai_core_sk_filepath: str

    @property
    def _llm_type(self) -> str:
        return "SAP OpenAI"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            "model_name": self.model_name,
            "deployment_url": self.deployment_url,
            "temperature": self.temperature,
            "ai_core_sk_filepath": self.ai_core_sk_filepath,
        }

    def _call(
        self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any
    ) -> str:
        endpoint = f"{self.deployment_url}/chat/completions?api-version=2023-05-15"
        headers = instantiation.get_headers(self.ai_core_sk_filepath)
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": f"{prompt}",
                }
            ],
            "temperature": self.temperature,
        }

        response = requests.post(endpoint, headers=headers, json=data)

        if not response.status_code == 200:
            logger.error(
                f"Invalid response from AI Core API with error code {response.status_code}"
            )
            raise Exception("Invalid response from AI Core API.")

        return self.parse(response.json())

    def parse(self, message) -> str:
        """Parse the returned JSON object from OpenAI."""
        return message["choices"][0]["message"]["content"]
