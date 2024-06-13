from typing import Any, List, Optional

import requests

from llm.models.sap_llm import SAPLLM, get_headers
from log.logger import logger


class OpenAI(SAPLLM):
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
