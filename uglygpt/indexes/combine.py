#!/usr/bin/env python3
# -*-coding:utf-8-*-

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from loguru import logger

from uglygpt.chains import LLMChain
from .base import Index
from .duckduckgo_search import DuckDuckGo
from .bing_search import BingSearch
from .arxiv import ArxivIndex
from .wiki import WikipediaSearch

@dataclass
class CombineSearch(Index):
    index_names: list[str] = field(default_factory=list)
    _indexes: list[Index] = field(default_factory=list)
    llm: LLMChain = field(init=False)

    def __post_init__(self):
        for index_name in self.index_names:
            try:
                index = globals()[index_name]()
                self._add_index(index)
            except:
                pass

    def search(self, query: str, n: int = Index.default_n) -> list[str]:
        logger.debug(f"{self._indexes}")
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda index: index.search(query, n), self._indexes)
        return [item for sublist in results for item in sublist]

    def _add_index(self, index: Index):
        self._indexes.append(index)

    def get(self, context: str) -> str:
        query = self.gen_search_query(context)
        logger.debug(f"query: {query}")
        search_result = self.search(query,5)
        logger.debug(f"search_result: {search_result}")
        # TODO: 这个Prompt需要改进，现在的返回结果并不是很好。
        llm = LLMChain("请根据你需要完成的任务：`{context}`，用中文整理搜索结果中的信息，只保留可能对你完成任务有帮助的信息。\n搜索结果如下：\n{result}")
        return llm(context = context, result = "\n".join(search_result))
        #return "\n".join(search_result)

    def gen_search_query(self, query: str) -> str:
        # TODO: 返回结果可能带引号，需要做处理。
        llm = LLMChain("你需要完成以下工作`{query}`。完成这项工作前，你可以通过多种搜索引擎获取一些有用的信息。根据你的工作任务，生成一个英文的搜索引擎的 Query，我将通过这个 Query 从搜索引擎中获得搜索结果。")
        return llm(query = query)