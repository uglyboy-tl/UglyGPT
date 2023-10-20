#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from dataclasses import dataclass

from .singleton import singleton

os.umask(22)

@singleton
@dataclass
class Config:
    """Singleton class for storing configuration settings.

    Attributes:
        BASE_LOG_DIR: Base directory for log files.
        openai_api_key: API key for OpenAI.
        openai_api_base: Base URL for OpenAI API.
        llm_provider: LLM provider name, default is "gpt4".
    """
    def __post_init__(self):
        """Post-initialization method.

        Sets default values for attributes.
        """
        self.BASE_LOG_DIR = 'logs'
        # API keys
        # OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_base = os.getenv("OPENAI_API_BASE")
        self.llm_provider = os.getenv("LLM_PROVIDER", "gpt4")
        # Bing Search
        self.bing_subscription_key = os.getenv("BING_SUBSCRIPTION_KEY")
        # Github
        self.github_token = os.getenv("GITHUB_TOKEN","")
        # Stop Words Dictionary
        self.stop_words_path = os.getenv("STOP_WORDS_PATH", "sources/baidu_stopwords.txt")


        self.feishu_webhook = os.getenv("FEISHU_WEBHOOK")
        self.feishu_secret = os.getenv("FEISHU_SECRET")
config = Config()
