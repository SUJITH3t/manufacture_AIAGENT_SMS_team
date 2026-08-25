"""
ManufacturingAgent Groq Cloud Provider
Integrates with Groq API (e.g. Llama 3.3 70B Versatile, Mixtral 8x7B) for ultra-low latency inference.
"""

import os
import logging
from typing import Optional
import httpx
from backend.app.providers.router import BaseLLMProvider, FallbackDeterministicProvider

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """Client for Groq Cloud API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 20.0
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.timeout = timeout
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"
        self._fallback = FallbackDeterministicProvider()

    def get_provider_name(self) -> str:
        return f"groq ({self.model})"

    def is_available(self) -> bool:
        """Check if Groq API key is present."""
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Send chat completion request to Groq."""
        if not self.is_available():
            return self._fallback.generate(prompt=prompt, system_prompt=system_prompt)

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1500
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(self.endpoint, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
                else:
                    logger.warning(f"Groq API error ({res.status_code}): {res.text}. Falling back.")
        except Exception as e:
            logger.warning(f"Groq request error ({e}). Falling back.")

        return self._fallback.generate(prompt=prompt, system_prompt=system_prompt)
