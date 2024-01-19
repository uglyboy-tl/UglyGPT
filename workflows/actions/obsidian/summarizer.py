#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import List, Dict

from loguru import logger

from ..mapsqlite import MapSqlite

ROLE = """
我在此提供一个 Github 项目的 Readme 文件，我希望你能帮我理解它。请阅读以下的文件内容，并从中提取出该项目的核心价值和主要功能。请注意，我不需要知道关于安装步骤、使用说明等详细信息，而是希望你能以300字以内的简洁语言，给我一个关于项目的核心概念和功能的总结，**注意请使用中文**。
"""
PROMPT_TEMPLATE = """
项目的描述(可能会对你总结项目有帮助)：
{description}

下面是项目的 Readme 文件：
## READMD.md
{readme}
"""

@dataclass
class ReadmeSummarizer(MapSqlite):
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE
    map_keys: List[str] = field(default_factory=lambda: ["readme", "description"])

    def run(self, name: List[str], readme_list: List[str], description_list: List[str]):
        logger.info("Running ReadmeSummarizer...")
        datas = self.ask(readme=readme_list, description=description_list)
        result ={}
        for k,v in zip(name, datas):
            if v == "Error":
                logger.error(f"Error when summarizing {k}")
                continue
            result[k] = v
        self._save(result)
        return result
