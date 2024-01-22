#!/usr/bin/env python3
# -*-coding:utf-8-*-

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

@dataclass
class BaseLanguageModel(ABC):
    """Base class for LLM providers.

    This class is an abstract base class (ABC) for LLM providers. It defines the common interface that all LLM providers should implement.

    Methods:
        set_role: Set Role message.
        ask: Ask a question and return the user's response.

    """

    delay_init: bool
    client: Any = field(init=False)
    model: str

    def __post_init__(self):
        if not self.delay_init:
            self.client = self._create_client()

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
    def generate(self, prompt: str = "") -> str:
        """Ask a question and return the user's response.

        Args:
            prompt: The question prompt.

        Returns:
            The user's response as a string.

        """
        pass

    @abstractmethod
    def completion_with_backoff(self, **kwargs):
        pass

    def _create_client(self):
        return None

    def _generate_validation(self):
        if self.delay_init:
            self.client = self._create_client()

    def _num_tokens(self, messages: list, model: str):
        """Calculate the number of tokens in a conversation.

        Args:
            messages: A list of messages in the conversation.
            model: The model to use for tokenization.

        Returns:
            The number of tokens in the conversation.
        """
        return 0

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        """Return the maximum number of tokens that can be returned at once.

        Returns:
            The maximum number of tokens that can be returned at once.

        """
        pass
