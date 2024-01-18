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
    # Bing Search
    bing_subscription_key: Optional[str] = os.getenv("BING_SUBSCRIPTION_KEY")
    # Github
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    # Stop Words Dictionary
    stop_words_path: str = os.getenv(
        "STOP_WORDS_PATH", "sources/baidu_stopwords.txt")

    feishu_webhook: Optional[str] = os.getenv("FEISHU_WEBHOOK")
    feishu_secret: Optional[str] = os.getenv("FEISHU_SECRET")


config = Config()