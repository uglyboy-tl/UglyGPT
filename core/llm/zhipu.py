#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from http import HTTPStatus

from zhipuai import ZhipuAI
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
    before_sleep_log
)
from loguru import logger

from core.base import config
from .base import LLMProvider
from .error import *

def not_notry_exception(exception: Exception):
    return False


@dataclass
class ChatGLM(LLMProvider):
    model: str = "glm-3-turbo"
    use_max_tokens: bool = False
    MAX_TOKENS: int = 128000
    temperature: float = 0.3
    messages: list = field(default_factory=list)

    def __post_init__(self):
        self._client = ZhipuAI(api_key=config.zhipuai_api_key)

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
            "do_sample": True,
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

        return self._client.chat.completions.create(**kwargs) # type: ignore

    @property
    def max_tokens(self):
        tokens = self._num_tokens(messages=self.messages, model=self.model) + 1000 # add 1000 tokens for answers
        if not self.MAX_TOKENS > tokens:
            raise Exception(f"Prompt is too long. This model's maximum context length is {self.MAX_TOKENS} tokens. your messages required {tokens} tokens")
        max_tokens = self.MAX_TOKENS - tokens + 1000
        return 2000 if max_tokens > 2000 else max_tokens
