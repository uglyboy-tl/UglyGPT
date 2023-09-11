#!/usr/bin/env python3
#-*-coding:utf-8-*-

from .base import LLMProvider
from uglygpt.base import config

supported_llm_providers = []

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

def get_llm_provider(llm_provider_name: str = None) -> LLMProvider:
    llm_provider_name = llm_provider_name or config.llm_provider
    """
    Get the LLM provider.

    Args:
        llm_provider_name: str

    Returns: LLMProvider
    """

    if llm_provider_name == "chatgpt":
        if not ChatGPT:
            print(
                "Error: OpenAILLM is not installed. Please install openai, tiktoken"
                " to use OpenAI as a LLM provider."
            )
        else:
            return ChatGPT(temperature=0.3)
    elif llm_provider_name == "gpt4":
        if not GPT4:
            print(
                "Error: OpenAILLM is not installed. Please install openai, tiktoken"
                " to use OpenAI as a LLM provider."
            )
        else:
            return GPT4(temperature=0.3)
    elif llm_provider_name == "huggingface":
        return None
    elif llm_provider_name == "bard":
        return None
    elif llm_provider_name == "palm":
        return None
    elif llm_provider_name == "fastchat":
        return None
    else:
        print("LLM provider not implemented")
        raise NotImplementedError("LLM provider not implemented")

__all__ = [
    "LLMProvider",
    "get_llm_provider",
    "supported_llm_providers",
]
