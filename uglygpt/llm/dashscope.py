#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from http import HTTPStatus

import dashscope
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
    before_sleep_log
)
from loguru import logger

from .base import LLMProvider
from uglygpt.base import config

dashscope.api_key = config.dashscope_api_key

class BadRequestError(Exception):
    pass

class Unauthorized(Exception):
    pass

class RequestLimitError(Exception):
    pass

def not_notry_exception(exception: Exception):
    if isinstance(exception, BadRequestError):
        return False
    if isinstance(exception, Unauthorized):
        return False
    return True


@dataclass
class DashScope(LLMProvider):
    model: str = dashscope.Generation.Models.qwen_max
    use_max_tokens: bool = True
    MAX_TOKENS: int = 6000
    seed: int = 1234
    messages: list = field(default_factory=list)

    def _num_tokens(self, messages: list, model: str):
        if model == "qwen-max" or model == "qwen-max-longcontext":
            logger.trace(
                "qwen-max may change over time. Returning num tokens assuming qwen-turbo.")
            return self._num_tokens(messages, model="qwen-turbo")
        try:
            response = dashscope.Tokenization.call(model=model, messages=messages)
        except KeyError:
            logger.trace("model not found. Using cl100k_base encoding.")
            response = dashscope.Tokenization.call(model="qwen-turbo", messages=messages)
        if response.status_code == HTTPStatus.OK:
            return response.usage["input_tokens"]
        else:
            raise Exception(
                f"Failed request_id: {response.request_id}, status_code: {response.status_code}, code: {response.code}, message:{response.message}")

    def set_role(self, msg: str) -> None:
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
        kwargs = {
            "model": self.model,
            "messages": self.messages,
            "seed": self.seed,
            "result_format": 'message'
        }
        try:
            if self.use_max_tokens:
                kwargs["max_tokens"] = 2000 if self.max_tokens>2000 else self.max_tokens
            response = self.completion_with_backoff(**kwargs)
        except Exception as e:
            if "Range of input length" in str(e) or "Prompt is too long." in str(e):
                if self.model == "qwen-max":
                    kwargs["model"] = "qwen-max-longcontext"
                logger.warning(
                    f"Model {self.model} does not support {self._num_tokens(self.messages, self.model)+1000} tokens. Trying again with {kwargs['model']}.")
                response = self.completion_with_backoff(**kwargs)
            else:
                raise e

        logger.trace(response)
        message = response.output.choices[0].message.content.strip()  # type: ignore
        return message

    @retry(retry=retry_if_exception(not_notry_exception), wait=wait_random_exponential(min=5, max=60), stop=stop_after_attempt(6), before_sleep=before_sleep_log(logger, "WARNING"))  # type: ignore
    def completion_with_backoff(self, **kwargs):
        """Make a completion request to the OpenAI API with exponential backoff.

        Args:
            **kwargs: Keyword arguments for the completion request.

        Returns:
            The completion response from the OpenAI API.
        """
        logger.trace(kwargs)
        response = dashscope.Generation.call(**kwargs)
        status_code, code, message = response.status_code, response.code, response.message # type: ignore
        if status_code == HTTPStatus.OK:
            return response
        elif status_code == 400:
            # 400 Bad Request
            raise BadRequestError(f"code: {code}, message:{message}")
        elif status_code == 401:
            # 401 Unauthorized
            raise Unauthorized()
        elif status_code == 429:
            # 404 Not Found
            raise RequestLimitError()
        else:
            raise Exception(
                f"Failed request_id: {response.request_id}, status_code: {status_code}, code: {code}, message:{message}") # type: ignore

    @property
    def max_tokens(self):
        # add 1000 tokens for answers
        tokens = self._num_tokens(
            messages=self.messages, model=self.model)
        if not self.MAX_TOKENS > tokens:
            raise Exception(
                f"Prompt is too long. This model's maximum context length is {self.MAX_TOKENS} tokens. your messages required {tokens} tokens")
        max_tokens = self.MAX_TOKENS - tokens
        return max_tokens
