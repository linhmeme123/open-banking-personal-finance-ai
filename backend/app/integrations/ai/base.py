from abc import ABC, abstractmethod


class AIProvider(ABC):
    provider_name: str

    @abstractmethod
    def generate_answer(
        self,
        message: str,
        financial_context: dict,
        chat_history: list[dict] | None = None,
    ) -> str:
        raise NotImplementedError
