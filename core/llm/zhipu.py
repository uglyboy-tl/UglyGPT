#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field

from zhipuai import ZhipuAI
from loguru import logger

from core.base import config
from .base import BaseLanguageModel
from .utils import retry_decorator

@dataclass
class ChatGLM(BaseLanguageModel):
    model: str = "glm-3-turbo"
    use_max_tokens: bool = False
    MAX_TOKENS: int = 128000
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
            "do_sample": True,
            "temperature": self.temperature,
        }

        if self.use_max_tokens:
            kwargs["max_tokens"] = self.max_tokens
        response = self.completion_with_backoff(**kwargs)

        logger.trace(f"kwargs:{kwargs}\nresponse:{response}")
        return response.choices[0].message.content.strip()  # type: ignore

    def _create_client(self):
        return ZhipuAI(api_key=config.zhipuai_api_key)

    @retry_decorator()
    def completion_with_backoff(self, **kwargs):
        return self.client.chat.completions.create(**kwargs) # type: ignore

    @property
    def max_tokens(self):
        tokens = self._num_tokens(messages=self.messages, model=self.model) + 1000 # add 1000 tokens for answers
        if not self.MAX_TOKENS > tokens:
            raise Exception(f"Prompt is too long. This model's maximum context length is {self.MAX_TOKENS} tokens. your messages required {tokens} tokens")
        max_tokens = self.MAX_TOKENS - tokens + 1000
        return 2000 if max_tokens > 2000 else max_tokens
