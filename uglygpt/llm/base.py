#!/usr/bin/env python3
#-*-coding:utf-8-*-

from abc import ABC,abstractmethod

class LLMProvider(ABC):
    """Base class for LLM providers."""

    def set_system(self, msg: str) -> None:
        pass

    @abstractmethod
    def ask(self, prompt: str) -> str:
        pass
