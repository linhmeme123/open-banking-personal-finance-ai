import logging

from app.core.config import settings
from app.integrations.ai.base import AIProvider
from app.integrations.ai.ollama_provider import OllamaAIProvider
from app.integrations.ai.openai_provider import OpenAIAIProvider
from app.integrations.ai.rule_based_provider import RuleBasedAIProvider


logger = logging.getLogger(__name__)

PROVIDERS: dict[str, type[AIProvider]] = {
    "rule_based": RuleBasedAIProvider,
    "ollama": OllamaAIProvider,
    "openai": OpenAIAIProvider,
}


def get_ai_provider() -> AIProvider:
    provider_name = settings.ai_provider.strip().lower()
    provider_class = PROVIDERS.get(provider_name)
    if not provider_class:
        logger.warning("Unknown AI provider '%s'; falling back to rule_based", settings.ai_provider)
        provider_class = RuleBasedAIProvider
    return provider_class()
