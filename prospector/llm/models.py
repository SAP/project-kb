import json
from typing import Any, List, Mapping, Optional

import requests
from dotenv import dotenv_values
from langchain_core.language_models.llms import LLM

from log.logger import logger


class SAPProvider(LLM):
    model_name: str
    deployment_url: str
    temperature: float

    @property
    def _llm_type(self) -> str:
        return "custom"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "model_name": self.model_name,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given input.

        Override this method to implement the LLM logic.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of the stop substrings.
                If stop tokens are not supported consider raising NotImplementedError.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            The model output as a string. Actual completions SHOULD NOT include the prompt.
        """
        if self.deployment_url is None:
            raise ValueError(
                "Deployment URL not set. Maybe you forgot to create the environment variable."
            )
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        return ""


class OpenAI(SAPProvider):
    def _call(
        self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any
    ) -> str:
        # Call super() to make sure model_name is valid
        super()._call(prompt, stop, **kwargs)
        # Model specific request data
        endpoint = f"{self.deployment_url}/chat/completions?api-version=2023-05-15"
        headers = get_headers()
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


class Gemini(SAPProvider):
    def _call(
        self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any
    ) -> str:
        # Call super() to make sure model_name is valid
        super()._call(prompt, stop, **kwargs)
        # Model specific request data
        endpoint = f"{self.deployment_url}/models/{self.model_name}:generateContent"
        headers = get_headers()
        data = {
            "generation_config": {
                "maxOutputTokens": 1000,
                "temperature": self.temperature,
            },
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            ],
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
        return message["candidates"][0]["content"]["parts"][0]["text"]


class Mistral(SAPProvider):
    def _call(
        self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any
    ) -> str:
        # Call super() to make sure model_name is valid
        super()._call(prompt, stop, **kwargs)
        # Model specific request data
        endpoint = f"{self.deployment_url}/chat/completions"
        headers = get_headers()
        data = {
            "model": "mistralai--mixtral-8x7b-instruct-v01",
            "max_tokens": 100,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
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


def get_headers():
    """Generate the request headers to use SAP AI Core. This method generates the authentication token and returns a Dict with headers.

    Returns:
        The headers object needed to send requests to the SAP AI Core.
    """
    with open(dotenv_values()["AI_CORE_KEY_FILEPATH"]) as f:
        sk = json.load(f)

    auth_url = f"{sk['url']}/oauth/token"
    client_id = sk["clientid"]
    client_secret = sk["clientsecret"]
    # api_base_url = f"{sk['serviceurls']['AI_API_URL']}/v2"

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
