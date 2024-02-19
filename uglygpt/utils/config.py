#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from dataclasses import dataclass
from typing import Optional

from .singleton import singleton


@singleton
@dataclass
class Config:
    # Github
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    feishu_webhook: Optional[str] = os.getenv("FEISHU_WEBHOOK")
    feishu_secret: Optional[str] = os.getenv("FEISHU_SECRET")


config = Config()
