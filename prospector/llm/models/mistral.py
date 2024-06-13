from typing import Any, List, Optional

import requests

from llm.models.sap_llm import SAPLLM, get_headers
from log.logger import logger


class Mistral(SAPLLM):
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
