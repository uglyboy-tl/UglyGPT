#!/usr/bin/env python3
# -*-coding:utf-8-*-

from .base import LLMProvider
from uglygpt.base import config

supported_llm_providers = []

try:
    from uglygpt.llm.gpt3 import GPT3
    supported_llm_providers.append(GPT3)
except ImportError:
    GPT3 = None

try:
    from uglygpt.llm.chatgpt import ChatGPT
    supported_llm_providers.append(ChatGPT)
except ImportError:
    ChatGPT = None


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
            return GPT3()
    elif llm_provider_name == "chatgpt":
        if not ChatGPT:
            raise NotImplementedError(
                "Error: OpenAILLM is not installed. Please install openai, tiktoken"
                " to use OpenAI as a LLM provider."
            )
        else:
            return ChatGPT()
    elif llm_provider_name == "chatgpt-16k":
        if not ChatGPT:
            raise NotImplementedError(
                "Error: OpenAILLM is not installed. Please install openai, tiktoken"
                " to use OpenAI as a LLM provider."
            )
        else:
            return ChatGPT(model="gpt-3.5-turbo-16k", MAX_TOKENS=16384)
    elif llm_provider_name == "gpt4":
        if not ChatGPT:
            raise NotImplementedError(
                "Error: OpenAILLM is not installed. Please install openai, tiktoken"
                " to use OpenAI as a LLM provider."
            )
        else:
            return ChatGPT(model="gpt-4", MAX_TOKENS=8192)
    elif llm_provider_name == "gpt4-32k":
        if not ChatGPT:
            raise NotImplementedError(
                "Error: OpenAILLM is not installed. Please install openai, tiktoken"
                " to use OpenAI as a LLM provider."
            )
        else:
            return ChatGPT(model="gpt-4-32k", MAX_TOKENS=32768)
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
