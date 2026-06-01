import logging

from app.core.config import settings
from app.integrations.ai.base import AIProvider
from app.integrations.ai.prompt import COACH_SYSTEM_PROMPT, build_context_prompt


logger = logging.getLogger(__name__)

PROVIDER_NOT_CONFIGURED_MESSAGE = "AI provider is not configured yet."
PROVIDER_UNAVAILABLE_MESSAGE = "OpenAI provider is currently unavailable."


class OpenAIAIProvider(AIProvider):
    provider_name = "openai"

    def generate_answer(
        self,
        message: str,
        financial_context: dict,
        chat_history: list[dict] | None = None,
    ) -> str:
        if not settings.openai_api_key:
            return PROVIDER_NOT_CONFIGURED_MESSAGE

        try:
            from openai import OpenAI

            client = OpenAI(api_key=settings.openai_api_key)
            response = client.responses.create(
                model=settings.openai_model,
                instructions=COACH_SYSTEM_PROMPT,
                input=[
                    {"role": "developer", "content": build_context_prompt(financial_context)},
                    *(chat_history or []),
                    {"role": "user", "content": message[:1000]},
                ],
                max_output_tokens=500,
            )
            return response.output_text.strip() or PROVIDER_UNAVAILABLE_MESSAGE
        except Exception:
            logger.exception("OpenAI Responses API request failed")
            return PROVIDER_UNAVAILABLE_MESSAGE
