#!/usr/bin/env python3
# -*-coding:utf-8-*-

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import json

from loguru import logger

from core import LLM
from .base import BaseRetriever
from . import *

@dataclass
class CombineRetriever(BaseRetriever):
    index_names: list[str] = field(default_factory=list)
    _indexes: list[BaseRetriever] = field(default_factory=list)

    def __post_init__(self):
        for index_name in self.index_names:
            try:
                index = globals()[index_name]()
                self._add_index(index)
            except:
                pass

    def search(self, query: str, n: int = BaseRetriever.default_n) -> list[str]:
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda index: index.search(query, n), self._indexes)
        return [item for sublist in results for item in sublist]

    def _add_index(self, index: BaseRetriever):
        self._indexes.append(index)

    def get(self, context: str) -> str:
        logger.debug(f"{self._indexes}")
        querys = self.gen_search_query(context)
        logger.debug(f"query: {querys}")
        search_result = []
        for query in querys:
            search_result.extend(self.search(query,5))
        logger.debug(f"search_result: {search_result}")
        # TODO: 这个Prompt需要改进，现在的返回结果并不是很好。
        llm = LLM("'''{result}'''使用上述信息，用中文详细回答以下问题或主题：“{context}”--请以报告的形式进行回答。报告应聚焦于问题的答案，结构严谨，信息丰富，深度分析，如果有实际数据和事实支持，那就更好了。报告的最低字数限制为1200字，并且需要使用markdown语法和APA格式。\n你必须基于给定的信息形成自己的具体而有效的观点。不要偏向于笼统且无意义的结论。\n在报告的最后，以APA格式写明所有引用的来源链接。")
        return llm(context = context, result = "\n".join(search_result))
        #return "\n".join(search_result)

    def gen_search_query(self, question: str) -> List[str]:
        # TODO: 返回结果可能带引号，需要做处理。
        llm = LLM(f'Write 3 bing search queries to search online that form an objective opinion from the following: "{{question}}"'\
            f'Use the current date if needed: {datetime.now().strftime("%B %d, %Y")}.\n' \
            f'The queries shoud be writing in English' \
            f'You must respond with a list of strings in the following format: ["query 1", "query 2", "query 3"].')
        return json.loads(llm(question = question))