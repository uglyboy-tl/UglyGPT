#!/usr/bin/env python3
#-*-coding:utf-8-*-

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

def tiktoken_len(text: str) -> int:
    encoding = tiktoken.encoding_for_model("text-davinci-003")
    return len(
        encoding.encode(text)
    )

@dataclass
class GPT3(LLMProvider):
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
class ChatGPT(LLMProvider):
    """GPT4 LLM provider."""
    requirements: list[str] = field(default_factory= lambda: ["openai","tictoken"])
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    MAX_TOKENS: int = 4096
    messages: list = field(default_factory= list)

    def _num_tokens(self, messages, model="gpt-3.5-turbo-0301"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.warning("model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo":
            logger.warning("gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
            return self._num_tokens(messages, model="gpt-3.5-turbo-0301")
        elif model == "gpt-4":
            logger.warning("gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
            return self._num_tokens(messages, model="gpt-4-0314")
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif model == "gpt-4-0314":
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(f"""num_tokens() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
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
        """Set the system."""
        self.messages = []
        if msg:
            self.messages.append({"role": "system", "content": msg})

    def ask(self, prompt: str) -> str:
        self.messages.append({"role": "user", "content": prompt})
        tokens = self._num_tokens(messages = self.messages, model=self.model)
        max_new_tokens = int(self.MAX_TOKENS) - tokens
        if max_new_tokens <= 0:
            raise ValueError(f"Prompt is too long. has {tokens} tokens, max is {self.MAX_TOKENS}")
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

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), before_sleep=before_sleep_log(logger,"WARNING"))
    def completion_with_backoff(self, **kwargs) -> str:
        return openai.ChatCompletion.create(**kwargs)

@dataclass
class GPT4(ChatGPT):
    model: str = "gpt-4"