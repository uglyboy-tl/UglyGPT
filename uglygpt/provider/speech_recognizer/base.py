"""Base class for LLM providers."""
from __future__ import annotations
import abc
from uglygpt.base import AbstractSingleton

class SpeechRecongnizerProvider(AbstractSingleton):
    @abc.abstractmethod
    def recognition(self, file_path: str, language: int) -> str:
        pass
