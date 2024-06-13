import json
from typing import Any, List, Mapping, Optional

import requests
from dotenv import dotenv_values
from langchain_core.language_models.llms import LLM

from log.logger import logger


class SAPLLM(LLM):
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
