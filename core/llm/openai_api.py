#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
import openai
from requests.exceptions import SSLError
from loguru import logger

from .base import BaseLanguageModel
from .utils import retry_decorator


def not_notry_exception(exception: BaseException) -> bool:
    if isinstance(exception, openai.BadRequestError):
        return False
    elif isinstance(exception, openai.AuthenticationError):
        return False
    elif isinstance(exception, openai.PermissionDeniedError):
        return False
    elif (
        isinstance(exception, openai.APIConnectionError)
        and exception.__cause__ is not None
        and isinstance(exception.__cause__, SSLError)
    ):
        return False
    else:
        return True


@dataclass
class ChatGPTAPI(BaseLanguageModel):
    model: str
    api_key: str
    base_url: str
    name: str
    use_max_tokens: bool = True
    MAX_TOKENS: int = 4096
    temperature: float = 0.3
    messages: list = field(default_factory=list)

    def generate(self, prompt: str) -> str:
        self._generate_validation()
        if len(self.messages) > 1:
            self.messages.pop()
        self.messages.append({"role": "user", "content": prompt})
        kwargs = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
        }

        if self.use_max_tokens:
            kwargs["max_tokens"] = self.max_tokens
        response = self.completion_with_backoff(**kwargs)

        logger.trace(f"kwargs:{kwargs}\nresponse:{response}")
        return response.choices[0].message.content.strip()  # type: ignore

    @retry_decorator(not_notry_exception)
    def completion_with_backoff(self, **kwargs):
        return self.client.chat.completions.create(**kwargs)

    def _create_client(self):
        return openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    @property
    def max_tokens(self):
        tokens = (
            self._num_tokens(messages=self.messages, model=self.model) + 1000
        )  # add 1000 tokens for answers
        if not self.MAX_TOKENS > tokens:
            raise Exception(
                f"Prompt is too long. This model's maximum context length is {self.MAX_TOKENS} tokens. your messages required {tokens} tokens"
            )
        max_tokens = self.MAX_TOKENS - tokens + 1000
        return max_tokens
