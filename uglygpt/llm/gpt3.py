#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
import openai
import tiktoken
from tenacity import (
    retry,
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
        default_factory=lambda: ["openai", "tictoken"])
    temperature: float = 0.3
    system_info = ""
    count_token: bool = True

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

    def ask(self, prompt: str) -> str:
        """Generate a response to a prompt.

        Args:
            prompt: The input prompt.

        Returns:
            The generated response.
        """
        prompt = f"{self.system_info}\n{prompt}"
        if self.count_token:
            tokens = self._num_tokens(prompt)
            max_new_tokens = int(4096) - tokens
            if max_new_tokens <= 0:
                raise ValueError(
                    f"Prompt is too long. has {tokens} tokens, max is 4096")
            completions = self.completion_with_backoff(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=max_new_tokens,
                temperature=self.temperature,
            )
        else:
            completions = self.completion_with_backoff(
                model="text-davinci-003",
                prompt=prompt,
                temperature=self.temperature,
            )
        message = completions.choices[0].text.strip()  # type: ignore
        logger.trace(message)
        return message

    @retry(wait=wait_random_exponential(min=5, max=60), stop=stop_after_attempt(6), before_sleep=before_sleep_log(logger, "WARNING"))  # type: ignore
    def completion_with_backoff(self, **kwargs):
        """Call the OpenAI Completion API with exponential backoff.

        Args:
            **kwargs: Keyword arguments for the API call.

        Returns:
            The response from the API call.
        """
        logger.trace(kwargs)
        return openai.Completion.create(**kwargs)