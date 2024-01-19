#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from openai import OpenAI
from openai import (
    BadRequestError,
    AuthenticationError,
    PermissionDeniedError,
    APIConnectionError,
)
from requests.exceptions import SSLError
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
    before_sleep_log
)
from loguru import logger

from .base import LLMProvider
from core.base import config

def not_notry_exception(exception: Exception):
    if isinstance(exception, BadRequestError):
        return False
    elif isinstance(exception, AuthenticationError):
        return False
    elif isinstance(exception, PermissionDeniedError):
        return False
    elif isinstance(exception, APIConnectionError) and exception.__cause__ is not None and isinstance(exception.__cause__, SSLError):
        return False
    else:
        return True

@dataclass
class ChatGPTAPI(LLMProvider):
    """A class representing a chat-based language model using OpenAI's GPT.

    Attributes:
        requirements: A list of required packages.
        model: The model to use for the language model.
        temperature: The temperature parameter for generating responses.
        MAX_TOKENS: The maximum number of tokens allowed in a conversation.
        messages: A list of messages in the conversation.
    """
    model: str
    api_key: str
    base_url: str
    name: str
    use_max_tokens: bool = True
    MAX_TOKENS: int = 4096
    temperature: float = 0.3
    messages: list = field(default_factory=list)

    def __post_init__(self):
        if not self.delay_init:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def ask(self, prompt: str) -> str:
        """Ask a question and get a response from the language model.

        Args:
            prompt: The user's prompt.

        Returns:
            The model's response.
        """
        if len(self.messages) > 1:
            self.messages.pop()
        self.messages.append({"role": "user", "content": prompt})
        kwargs = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
        }
        try:
            if self.use_max_tokens:
                kwargs["max_tokens"] = self.max_tokens
            response = self.completion_with_backoff(**kwargs)
        except Exception as e:
                raise e

        logger.trace(kwargs)
        logger.trace(response)
        return response.choices[0].message.content.strip()  # type: ignore

    @retry(retry=retry_if_exception(not_notry_exception), wait=wait_random_exponential(min=5, max=60), stop=stop_after_attempt(6), before_sleep=before_sleep_log(logger, "WARNING"))  # type: ignore
    def completion_with_backoff(self, **kwargs):
        """Make a completion request to the OpenAI API with exponential backoff.

        Args:
            **kwargs: Keyword arguments for the completion request.

        Returns:
            The completion response from the OpenAI API.
        """
        if self.delay_init:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client.chat.completions.create(**kwargs)


    @property
    def max_tokens(self):
        tokens = self._num_tokens(messages=self.messages, model=self.model) + 1000 # add 1000 tokens for answers
        if not self.MAX_TOKENS > tokens:
            raise Exception(f"Prompt is too long. This model's maximum context length is {self.MAX_TOKENS} tokens. your messages required {tokens} tokens")
        max_tokens = self.MAX_TOKENS - tokens + 1000
        return max_tokens
