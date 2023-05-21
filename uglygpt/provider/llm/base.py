"""Base class for LLM providers."""
from __future__ import annotations
import abc
from uglygpt.base import AbstractSingleton

class LLMProvider(AbstractSingleton):
    @abc.abstractmethod
    def instruct(self, prompt: str, tokens: int) -> str:
        pass
