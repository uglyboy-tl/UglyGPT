"""Base class for LLM providers."""
import abc
from uglygpt.base import AbstractSingleton

class LLMProvider(AbstractSingleton):
    @abc.abstractmethod
    def instruct(self, prompt: str, tokens: int) -> str:
        pass
