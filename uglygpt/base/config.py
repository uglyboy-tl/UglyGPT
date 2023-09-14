#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from dataclasses import dataclass

from .singleton import singleton


@singleton
@dataclass
class Config:
    def __post_init__(self):
        self.BASE_LOG_DIR = 'logs'
        # API keys
        # OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_base = os.getenv("OPENAI_API_BASE")
        self.llm_provider = os.getenv("LLM_PROVIDER", "gpt4")


config = Config()
