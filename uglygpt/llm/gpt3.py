#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
import openai
from openai.error import (
    APIError,
    AuthenticationError,
    InvalidRequestError
)
import tiktoken
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_random_exponential,
    before_sleep_log
)  # for exponential backoff
from loguru import logger

from .base import LLMProvider
from uglygpt.base import config

# Initialize the OpenAI API client
openai.api_key = config.openai_api_key
openai.api_base = config.openai_api_base


@dataclass
class GPT3(LLMProvider):
    """GPT3 LLM provider.

    Attributes:
        requirements: A list of required modules.
        temperature: The temperature value for generating responses.
    """
    requirements: list[str] = field(
        default_factory=lambda: ["openai", "tiktoken"])
    temperature: float = 0.3
    MAX_TOKENS: int = 4096
    system_info = ""
    use_max_tokens: bool = True

    def _num_tokens(self, prompt: str) -> int:
        """Calculate the number of tokens in a prompt.

        Args:
            prompt: The input prompt.

        Returns:
            The number of tokens in the prompt.
        """
        encoding = tiktoken.encoding_for_model("text-davinci-003")
        num_tokens = len(encoding.encode(prompt))
        return num_tokens

    def set_system(self, msg: str) -> None:
        """Set the system message.

        Args:
            msg: The message to set.

        Returns:
            None
        """
        self.system_info = msg
        self.prompt = self.system_info

    def ask(self, prompt: str) -> str:
        """Generate a response to a prompt.

        Args:
            prompt: The input prompt.

        Returns:
            The generated response.
        """
        self.prompt = f"{self.system_info}\n{prompt}"
        kwargs = {
            "model": "text-davinci-003",
            "prompt": self.prompt,
            "temperature": self.temperature,
        }
        if self.use_max_tokens:
            kwargs["max_tokens"] = self.max_tokens
        completions = self.completion_with_backoff(**kwargs)
        message = completions.choices[0].text.strip()  # type: ignore
        logger.trace(message)
        return message

    @retry(retry=retry_if_not_exception_type(exception_types=(APIError, AuthenticationError, InvalidRequestError)), wait=wait_random_exponential(min=5, max=60), stop=stop_after_attempt(6), before_sleep=before_sleep_log(logger, "WARNING"))  # type: ignore
    def completion_with_backoff(self, **kwargs):
        """Call the OpenAI Completion API with exponential backoff.

        Args:
            **kwargs: Keyword arguments for the API call.

        Returns:
            The response from the API call.
        """
        logger.trace(kwargs)
        return openai.Completion.create(**kwargs)

    @property
    def max_tokens(self):
        tokens = self._num_tokens(self.prompt)
        assert self.MAX_TOKENS > tokens, f"Prompt is too long. has {tokens} tokens, max is {self.MAX_TOKENS}"
        return self.MAX_TOKENS - tokens
