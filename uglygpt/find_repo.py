#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import cast

from loguru import logger
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.query_engine import CitationQueryEngine
import nest_asyncio

from uglychain import Model, Retriever, StorageRetriever
from uglychain.storage import Storage, SQLiteStorage
from uglychain.llm.llama_index import LlamaIndexLLM

import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

nest_asyncio.apply()
Settings.llm = LlamaIndexLLM(model = Model.GPT3_TURBO)

@dataclass
class GithubIndex():
    filename: str = "data/github/github.db"
    model: Model = Model.DEFAULT
    summarizer_db: Storage = field(init=False)
    retriever: StorageRetriever = field(init=False)

    def __post_init__(self):
        self.summarizer_db = SQLiteStorage(self.filename, "ReadmeSummarizer", 30)
        self.retriever = Retriever.LlamaIndex.getStorage(persist_dir="./data/github/repos")
        if self._need_update:
            self._update()

    def search(self, query: str):
        index = cast(VectorStoreIndex, self.retriever.index) # type: ignore
        query_engine = CitationQueryEngine.from_args(index, similarity_top_k=5)
        #query_engine = index.as_query_engine(llm=LlamaIndexLLM(Model.GPT3_TURBO), similarity_top_k=8) # type: ignore
        return query_engine.query(query)
        #self.retriever.get(query, "refine")

    @property
    def _need_update(self):
        return False

    def _update(self):
        doc_chunks = []
        data = self.summarizer_db.load(condition = "timestamp = date(\'now\',\'localtime\')")
        for key, value in data.items():
            doc = Document(text=value, doc_id=key)
            doc_chunks.append(doc)
        index = cast(VectorStoreIndex, self.retriever.index) # type: ignore
        logger.info("refresh_ref_docs")
        index.refresh_ref_docs(doc_chunks)
        self.retriever.storage.save(index)
        logger.info("refresh_ref_docs done")

if __name__ == "__main__":
    index = GithubIndex()
    result = index.search("给我介绍几个关于使用大模型自动写代码的项目吧！")
    #logger.debug(result.source_nodes)
    logger.info(result)
