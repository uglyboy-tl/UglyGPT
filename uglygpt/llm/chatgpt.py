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
class ChatGPT(LLMProvider):
    """A class representing a chat-based language model using OpenAI's GPT.

    Attributes:
        requirements: A list of required packages.
        model: The model to use for the language model.
        temperature: The temperature parameter for generating responses.
        MAX_TOKENS: The maximum number of tokens allowed in a conversation.
        messages: A list of messages in the conversation.
    """
    requirements: list[str] = field(
        default_factory=lambda: ["openai", "tictoken"])
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.3
    MAX_TOKENS: int = 4096
    messages: list = field(default_factory=list)
    count_token: bool = False

    def _num_tokens(self, messages, model="gpt-3.5-turbo-0301"):
        """Calculate the number of tokens in a conversation.

        Args:
            messages: A list of messages in the conversation.
            model: The model to use for tokenization.

        Returns:
            The number of tokens in the conversation.
        """
        if model == "gpt-3.5-turbo":
            logger.trace(
                "gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
            return self._num_tokens(messages, model="gpt-3.5-turbo-0301")
        elif model == "gpt-4":
            logger.trace(
                "gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
            return self._num_tokens(messages, model="gpt-4-0314")
        elif model == "gpt-3.5-turbo-0301":
            # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_message = 4
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif model == "gpt-4-0314":
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(
                f"""num_tokens() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.trace("model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def set_system(self, msg: str) -> None:
        """Set the system message in the conversation.

        Args:
            msg: The system message.
        """
        self.messages = []
        if msg:
            self.messages.append({"role": "system", "content": msg})

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
        if self.count_token:
            max_new_tokens = self.max_token
            response = self.completion_with_backoff(
                model=self.model,
                messages=self.messages,
                max_tokens=max_new_tokens,
                temperature=self.temperature,
            )
        else:
            response = self.completion_with_backoff(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
            )
        logger.trace(response)
        message = response.choices[0].message.content.strip() # type: ignore
        return message

    @retry(wait=wait_random_exponential(min=5, max=60), stop=stop_after_attempt(6), before_sleep=before_sleep_log(logger, "WARNING"))  # type: ignore
    def completion_with_backoff(self, **kwargs):
        """Make a completion request to the OpenAI API with exponential backoff.

        Args:
            **kwargs: Keyword arguments for the completion request.

        Returns:
            The completion response from the OpenAI API.
        """
        logger.trace(kwargs)
        return openai.ChatCompletion.create(**kwargs)

    @property
    def max_token(self):
        tokens = self._num_tokens(messages=self.messages, model=self.model)
        assert self.MAX_TOKENS > tokens , f"Prompt is too long. has {tokens} tokens, max is {self.MAX_TOKENS}"
        return self.MAX_TOKENS - tokens