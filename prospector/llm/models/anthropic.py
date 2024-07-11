from typing import Any, Dict, List, Optional

import requests
from langchain_core.language_models.llms import LLM

import llm.instantiation as instantiation
from log.logger import logger


class Anthropic(LLM):
    model_name: str
    deployment_url: str
    temperature: float
    ai_core_sk_filepath: str

    @property
    def _llm_type(self) -> str:
        return "SAP Anthropic"

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
        endpoint = f"{self.deployment_url}/invoke"
        headers = instantiation.get_headers(self.ai_core_sk_filepath)
        data = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": f"{prompt}",
                }
            ],
            "temperature": self.temperature,
        }

        try:
            response = requests.post(endpoint, headers=headers, json=data)
            response.raise_for_status()
            return self.parse(response.json())
        except requests.exceptions.HTTPError as http_error:
            logger.error(
                f"HTTP error occurred when sending a request through AI Core: {http_error}"
            )
            raise
        except requests.exceptions.Timeout as timeout_err:
            logger.error(
                f"Timeout error occured when sending a request through AI Core: {timeout_err}"
            )
            raise
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(
                f"Connection error occurred when sending a request through AI Core: {conn_err}"
            )
            raise
        except requests.exceptions.RequestException as req_err:
            logger.error(
                f"A request error occured when sending a request through AI Core: {req_err}"
            )
            raise

    def parse(self, message) -> str:
        """Parse the returned JSON object from OpenAI."""
        return message["content"][0]["text"]
