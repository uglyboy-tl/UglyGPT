#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from dataclasses import dataclass
from typing import Optional

from .singleton import singleton


@singleton
@dataclass
class Config:
    BASE_LOG_DIR = 'logs'
    # API keys
    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_api_base: str = os.getenv(
        "OPENAI_API_BASE", "https://api.openai.com/v1")
    copilot_token: Optional[str] = os.getenv("COPILOT_TOKEN")
    copilot_gpt4_service_url: Optional[str] = os.getenv(
        "COPILOT_GPT4_SERVICE_URL")
    llm_provider: str = os.getenv("LLM_PROVIDER", "gpt4")


config = Config()
