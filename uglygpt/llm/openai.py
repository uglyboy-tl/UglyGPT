#!/usr/bin/env python3
#-*-coding:utf-8-*-

from dataclasses import dataclass, field
import openai
from openai.error import RateLimitError
import tiktoken
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    before_log
)  # for exponential backoff
from loguru import logger

from .base import LLMProvider
from uglygpt.base import config

# Initialize the OpenAI API client
openai.api_key = config.openai_api_key
openai.api_base = config.openai_api_base

def tiktoken_len(text: str) -> int:
    encoding = tiktoken.encoding_for_model("text-davinci-003")
    return len(
        encoding.encode(text)
    )

@dataclass
class ChatGPT(LLMProvider):
    """ChatGPT LLM provider."""
    temperature: float = 0.7

    def _num_tokens(self, prompt: str) -> int:
        num_tokens = tiktoken_len(prompt)
        return num_tokens

    def ask(self, prompt: str) -> str:
        tokens = self._num_tokens(prompt)
        max_new_tokens = int(4096) - tokens
        if max_new_tokens <= 0:
            raise ValueError(f"Prompt is too long. has {tokens} tokens, max is 4096")
        logger.debug(prompt)
        completions = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=max_new_tokens,
            temperature=self.temperature,
        )
        message = completions.choices[0].text
        logger.debug(message)
        return message

@dataclass
class GPT4(LLMProvider):
    """GPT4 LLM provider."""
    requirements: list[str] = field(default_factory= lambda: ["openai","tictoken"])
    model: str = "gpt-4"
    temperature: float = 0.7
    MAX_TOKENS: int = 4096
    messages: list = field(default_factory= list)

    def _num_tokens(self, prompt: str) -> int:
        num_tokens = tiktoken_len(prompt)
        return num_tokens

    def set_system(self, msg: str) -> None:
        """Set the system."""
        self.messages = []
        if msg:
            self.messages.append({"role": "system", "content": msg})

    def ask(self, prompt: str) -> str:
        tokens = self._num_tokens(prompt)
        max_new_tokens = int(self.MAX_TOKENS) - tokens
        if max_new_tokens <= 0:
            raise ValueError(f"Prompt is too long. has {tokens} tokens, max is {self.MAX_TOKENS}")
        self.messages.append({"role": "user", "content": prompt})
        logger.trace(self.messages)
        response = self.completion_with_backoff(
            model=self.model,
            messages=self.messages,
            max_tokens=max_new_tokens,
            temperature=self.temperature,
        )
        message = response.choices[0]['message']['content']
        logger.trace(response.choices[0]['message'])
        return message

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), before=before_log(logger,"WARNING"))
    def completion_with_backoff(self, **kwargs) -> str:
        return openai.ChatCompletion.create(**kwargs)