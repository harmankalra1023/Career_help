from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract interface for LLM calls (Technical Design §1 & §3.8)."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        pass


class MockLLM(LLMClient):
    """Deterministic mock client for offline tests and development."""

    async def generate(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        logger.info("Using MockLLM generator")
        if schema:
            return json.dumps({
                "narrative": "Profile demonstrates solid trajectory towards Backend Engineering.",
                "confidence": 0.85,
                "recommendations": ["Advance Docker containerization", "Deepen PostgreSQL query tuning"]
            })
        return "Profile demonstrates solid trajectory towards Backend Engineering. Prioritize containerization and distributed databases."


class GroqLLM(LLMClient):
    """
    Groq Cloud LLM provider (ultra-low latency Llama-3.3-70b, Llama-3.1-8b).
    Connects to the OpenAI-compatible endpoint at https://api.groq.com/openai/v1.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or settings.GROQ_API_KEY or settings.LLM_API_KEY
        self.model = model or settings.GROQ_MODEL or settings.LLM_MODEL or "llama-3.3-70b-versatile"
        self.base_url = (base_url or settings.GROQ_BASE_URL or "https://api.groq.com/openai/v1").rstrip("/")

    async def generate(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        if not self.api_key or "your_" in self.api_key.lower():
            logger.warning("Groq API key not configured. Falling back to MockLLM response.")
            return await MockLLM().generate(prompt, schema, system_prompt)

        default_system = (
            "You are the Digital Career Twin AI intelligence assistant. "
            "You provide objective, evidence-grounded skill evaluations, gap analysis, "
            "and career path recommendations. Never invent unverified credentials."
        )

        messages = [
            {"role": "system", "content": system_prompt or default_system},
            {"role": "user", "content": prompt}
        ]

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1500,
        }

        if schema:
            payload["response_format"] = {"type": "json_object"}
            messages[0]["content"] += "\nYou MUST return valid JSON conforming to the requested structure."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return content
            except httpx.HTTPStatusError as e:
                logger.error(f"Groq API HTTP error {e.response.status_code}: {e.response.text}")
                raise RuntimeError(f"Groq API error ({e.response.status_code}): {e.response.text}") from e
            except Exception as e:
                logger.error(f"Groq API request failed: {e}")
                raise RuntimeError(f"Groq API request failed: {e}") from e


def get_llm_client() -> LLMClient:
    """Factory to retrieve configured LLMClient based on settings."""
    provider = settings.LLM_PROVIDER.lower()
    if provider == "groq":
        return GroqLLM()
    elif provider == "mock":
        return MockLLM()
    else:
        # Default fallback to Groq if key is present, otherwise MockLLM
        if settings.GROQ_API_KEY:
            return GroqLLM()
        return MockLLM()
