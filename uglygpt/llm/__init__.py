#!/usr/bin/env python3
# -*-coding:utf-8-*-

from .base import LLMProvider
from uglygpt.base import config

supported_llm_providers = []

try:
    from uglygpt.llm.openai import GPT3
    supported_llm_providers.append(GPT3)
except ImportError:
    ChatGPT = None

try:
    from uglygpt.llm.openai import ChatGPT
    supported_llm_providers.append(ChatGPT)
except ImportError:
    ChatGPT = None

try:
    from uglygpt.llm.openai import GPT4
    supported_llm_providers.append(GPT4)
except ImportError:
    GPT4 = None


def get_llm_provider(llm_provider_name: str = "") -> LLMProvider:
    """
    Get the LLM provider.

    Args:
        llm_provider_name: The name of the LLM provider.

    Returns:
        The LLMProvider object.
    """

    if llm_provider_name == "":
        llm_provider_name = config.llm_provider

    if llm_provider_name == "gpt3":
        if not GPT3:
            raise NotImplementedError(
                "Error: OpenAILLM is not installed. Please install openai, tiktoken"
                " to use OpenAI as a LLM provider."
            )
        else:
            return GPT3(temperature=0.3)
    elif llm_provider_name == "chatgpt":
        if not ChatGPT:
            raise NotImplementedError(
                "Error: OpenAILLM is not installed. Please install openai, tiktoken"
                " to use OpenAI as a LLM provider."
            )
        else:
            return ChatGPT(temperature=0.3)
    elif llm_provider_name == "gpt4":
        if not GPT4:
            raise NotImplementedError(
                "Error: OpenAILLM is not installed. Please install openai, tiktoken"
                " to use OpenAI as a LLM provider."
            )
        else:
            return GPT4(temperature=0.3)
    elif llm_provider_name == "huggingface":
        raise NotImplementedError("Huggingface LLM provider not implemented")
    elif llm_provider_name == "bard":
        raise NotImplementedError("Bard LLM provider not implemented")
    elif llm_provider_name == "palm":
        raise NotImplementedError("Palm LLM provider not implemented")
    elif llm_provider_name == "fastchat":
        raise NotImplementedError("Fastchat LLM provider not implemented")
    else:
        print("LLM provider not implemented")
        raise NotImplementedError("LLM provider not implemented")


__all__ = [
    "LLMProvider",
    "get_llm_provider",
    "supported_llm_providers",
]
