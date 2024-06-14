from typing import Any, List, Optional

import requests

from llm.models.sap_llm import SAPLLM, get_headers
from log.logger import logger


class Gemini(SAPLLM):
    def _call(
        self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any
    ) -> str:
        # Call super() to make sure model_name is valid
        super()._call(prompt, stop, **kwargs)
        # Model specific request data
        endpoint = f"{self.deployment_url}/models/{self.model_name}:generateContent"
        headers = get_headers(self.ai_core_sk_file_path)
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
