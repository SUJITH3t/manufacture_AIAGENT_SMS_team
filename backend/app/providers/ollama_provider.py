"""
ManufacturingAgent Ollama Provider
Integrates with local Ollama instance (e.g. Llama 3, Mistral, Gemma).
"""

import os
import logging
from typing import Optional
import httpx
from backend.app.providers.router import BaseLLMProvider, FallbackDeterministicProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Client for local Ollama REST API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0
    ):
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3:8b")
        self.timeout = timeout
        self._fallback = FallbackDeterministicProvider()

    def get_provider_name(self) -> str:
        return f"ollama ({self.model})"

    def is_available(self) -> bool:
        """Check if local Ollama daemon is active."""
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Send generation request to Ollama endpoint."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()
                else:
                    logger.warning(f"Ollama API returned HTTP {res.status_code}: {res.text}. Utilizing fallback.")
        except Exception as e:
            logger.warning(f"Ollama connection error ({e}). Utilizing fallback.")

        return self._fallback.generate(prompt=prompt, system_prompt=system_prompt)
