#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from dataclasses import dataclass
from typing import Optional

from .singleton import singleton


@singleton
@dataclass
class Config:
    # API keys
    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_api_base: str = os.getenv(
        "OPENAI_API_BASE", "https://api.openai.com/v1")
    copilot_token: Optional[str] = os.getenv("COPILOT_TOKEN")
    copilot_gpt4_service_url: Optional[str] = os.getenv(
        "COPILOT_GPT4_SERVICE_URL")
    # Dashscope
    dashscope_api_key: Optional[str] = os.getenv("DASHSCOPE_API_KEY")
    # Zhipuai
    zhipuai_api_key: Optional[str] = os.getenv("ZHIPUAI_API_KEY")
    llm_provider: str = os.getenv("LLM_PROVIDER", "gpt4")


config = Config()
