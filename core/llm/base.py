#!/usr/bin/env python3
# -*-coding:utf-8-*-

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class LLMProvider(ABC):
    """Base class for LLM providers.

    This class is an abstract base class (ABC) for LLM providers. It defines the common interface that all LLM providers should implement.

    Methods:
        set_role: Set Role message.
        ask: Ask a question and return the user's response.

    """
    delay_init: bool

    def _num_tokens(self, messages: list, model: str):
        return 0

    def set_role(self, msg: str) -> None:
        """Set the system message.

        Args:
            msg: The message to set.

        Returns:
            None

        """
        self.messages = []
        if msg:
            self.messages.append({"role": "system", "content": msg})

    @abstractmethod
    def ask(self, prompt: str) -> str:
        """Ask a question and return the user's response.

        Args:
            prompt: The question prompt.

        Returns:
            The user's response as a string.

        """
        pass

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        """Return the maximum number of tokens that can be returned at once.

        Returns:
            The maximum number of tokens that can be returned at once.

        """
        pass