#!/usr/bin/env python3
# -*-coding:utf-8-*-

from core.base import config
from core.llm.base import BaseLanguageModel

try:
    from .chatgpt import ChatGPT
    from .copilot import Copilot
    from .yi import Yi
except ImportError:
    ChatGPT = None
    Copilot = None
    Yi = None

try:
    from .dashscope import DashScope
except ImportError:
    DashScope = None

try:
    from .zhipu import ChatGLM
except ImportError:
    ChatGLM = None

LLM_PROVIDERS = {
    "gpt-3.5-turbo": (ChatGPT, {"model": "gpt-3.5-turbo-1106", "MAX_TOKENS": 4096}),
    "gpt-3.5-turbo-16k": (ChatGPT, {"model": "gpt-3.5-turbo-16k", "MAX_TOKENS": 16384}),
    "gpt-4": (ChatGPT, {"model": "gpt-4", "MAX_TOKENS": 8192}),
    "gpt-4-32k": (ChatGPT, {"model": "gpt-4-32k", "MAX_TOKENS": 32768}),
    "gpt-4-turbo": (ChatGPT, {"model": "gpt-4-1106-preview", "MAX_TOKENS": 128000}),
    "copilot-3.5": (Copilot, {"model": "gpt-3.5-turbo"}),
    "copilot-4": (Copilot, {"model": "gpt-4"}),
    "yi": (Yi, {"model": "yi-34b-chat-v08"}),
    "yi-32k": (Yi, {"model": "yi-34b-chat-32k-v01"}),
    "qwen": (DashScope, {"model": "qwen-max", "MAX_TOKENS": 6000}),
    "qwen-turbo": (DashScope, {"model": "qwen-turbo", "MAX_TOKENS": 6000}),
    "qwen-plus": (DashScope, {"model": "qwen-plus", "MAX_TOKENS": 30000}),
    "qwen-28k": (DashScope, {"model": "qwen-max-longcontext", "MAX_TOKENS": 28000}),
    "glm-4": (ChatGLM, {"model": "glm-4", "MAX_TOKENS": 128000}),
    "glm-3": (ChatGLM, {"model": "glm-3-turbo", "MAX_TOKENS": 128000}),
}

ERROR_MSG = "Error: {provider} is not installed. Please install required packages to use {provider} as a LLM provider."


def get_llm_provider(
    llm_provider_name: str = config.llm_provider, is_init_delay: bool = False
) -> BaseLanguageModel:
    """
    Get the LLM provider.

    Args:
        llm_provider_name: The name of the LLM provider.

    Returns:
        The LLMProvider object.
    """

    if llm_provider_name in LLM_PROVIDERS.keys():
        provider, kwargs = LLM_PROVIDERS[llm_provider_name]
        kwargs["is_init_delay"] = is_init_delay
        if provider is None:
            raise NotImplementedError(ERROR_MSG.format(provider=llm_provider_name))
        else:
            return provider(**kwargs)
    else:
        raise NotImplementedError(f"{llm_provider_name} LLM provider not implemented")

__all__ = ["get_llm_provider"]