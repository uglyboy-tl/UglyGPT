#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from dataclasses import dataclass
from typing import Optional

from .singleton import singleton


@singleton
@dataclass
class Config:
    # Bing Search
    bing_subscription_key: Optional[str] = os.getenv("BING_SUBSCRIPTION_KEY")
    # Stop Words Dictionary
    stop_words_path: str = os.getenv("STOP_WORDS_PATH", "sources/baidu_stopwords.txt")


config = Config()
