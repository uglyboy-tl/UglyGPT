#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from http import HTTPStatus

import dashscope
from loguru import logger

from core.base import config
from .base import BaseLanguageModel
from .utils import retry_decorator


dashscope.api_key = config.dashscope_api_key


class BadRequestError(Exception):
    pass


class Unauthorized(Exception):
    pass


class RequestLimitError(Exception):
    pass


def not_notry_exception(exception: BaseException):
    if isinstance(exception, BadRequestError):
        return False
    if isinstance(exception, Unauthorized):
        return False
    return True


@dataclass
class DashScope(BaseLanguageModel):
    model: str = dashscope.Generation.Models.qwen_max
    MAX_TOKENS: int = 6000
    seed: int = 1234
    messages: list = field(default_factory=list)

    def generate(self, prompt: str) -> str:
        self._generate_validation()
        if len(self.messages) > 1:
            self.messages.pop()
        self.messages.append({"role": "user", "content": prompt})
        kwargs = {
            "model": self.model,
            "messages": self.messages,
            "seed": self.seed,
            "result_format": "message",
        }
        try:
            response = self.completion_with_backoff(**kwargs)
        except Exception as e:
            if "Range of input length" in str(e) or "Prompt is too long." in str(e):
                if self.model == "qwen-max":
                    kwargs["model"] = "qwen-max-longcontext"
                else:
                    raise e
                logger.warning(
                    f"Model {self.model} does not support {self._num_tokens(self.messages, self.model)} tokens. Trying again with {kwargs['model']}."
                )
                response = self.completion_with_backoff(**kwargs)
            else:
                raise e

        logger.trace(f"kwargs:{kwargs}\nresponse:{response}")
        return response.output.choices[0].message.content.strip()  # type: ignore

    @retry_decorator(not_notry_exception)
    def completion_with_backoff(self, **kwargs):
        response = dashscope.Generation.call(**kwargs)

        status_code, code, message = (
            response.status_code, # type: ignore
            response.code, # type: ignore
            response.message, # type: ignore
        )
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
                f"Failed request_id: {response.request_id}, status_code: {status_code}, code: {code}, message:{message}"  # type: ignore
            )

    def _num_tokens(self, messages: list, model: str):
        if model == "qwen-max" or model == "qwen-max-longcontext":
            logger.trace(
                "qwen-max may change over time. Returning num tokens assuming qwen-turbo."
            )
            return self._num_tokens(messages, model="qwen-turbo")
        try:
            response = dashscope.Tokenization.call(model=model, messages=messages)
        except KeyError:
            logger.trace("model not found. Using qwen-turbo encoding.")
            response = dashscope.Tokenization.call(
                model="qwen-turbo", messages=messages
            )
        if response.status_code == HTTPStatus.OK:
            return response.usage["input_tokens"]
        else:
            raise Exception(
                f"Failed request_id: {response.request_id}, status_code: {response.status_code}, code: {response.code}, message:{response.message}"
            )

    @property
    def max_tokens(self):
        # add 1000 tokens for answers
        tokens = self._num_tokens(messages=self.messages, model=self.model)
        if not self.MAX_TOKENS > tokens:
            raise Exception(
                f"Prompt is too long. This model's maximum context length is {self.MAX_TOKENS} tokens. your messages required {tokens} tokens"
            )
        max_tokens = self.MAX_TOKENS - tokens
        return max_tokens
