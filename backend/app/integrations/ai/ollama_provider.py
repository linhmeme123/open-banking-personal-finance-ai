import logging

import httpx

from app.core.config import settings
from app.integrations.ai.base import AIProvider
from app.integrations.ai.prompt import COACH_SYSTEM_PROMPT, build_context_prompt


logger = logging.getLogger(__name__)

PROVIDER_UNAVAILABLE_MESSAGE = "Ollama provider is currently unavailable."


class OllamaAIProvider(AIProvider):
    provider_name = "ollama"

    def generate_answer(
        self,
        message: str,
        financial_context: dict,
        chat_history: list[dict] | None = None,
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": f"{COACH_SYSTEM_PROMPT}\n\n{build_context_prompt(financial_context)}",
            },
            *(chat_history or []),
            {"role": "user", "content": message[:1000]},
        ]
        try:
            response = httpx.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                json={"model": settings.ollama_model, "messages": messages, "stream": False},
                timeout=30,
            )
            response.raise_for_status()
            answer = response.json().get("message", {}).get("content", "").strip()
            return answer or PROVIDER_UNAVAILABLE_MESSAGE
        except (httpx.HTTPError, ValueError, TypeError):
            logger.exception("Ollama API request failed")
            return PROVIDER_UNAVAILABLE_MESSAGE
