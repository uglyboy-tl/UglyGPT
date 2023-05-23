from __future__ import annotations
import pinecone

from typing import Any, Dict, List

from uglygpt.indexes.base import BaseIndex
from uglygpt.provider import get_embedding_provider

class Pinecone(BaseIndex):
    def __init__(self, cfg, memory_index = None):
        pinecone_api_key = cfg.pinecone_api_key
        pinecone_region = cfg.pinecone_region
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_region)
        self.memory = get_embedding_provider()

        self.table_name = memory_index or cfg.memory_index
        dimension = 1536
        metric = "cosine"
        pod_type = "p1"
        # this assumes we don't start with memory.
        # for now this works.
        # we'll need a more complicated and robust system if we want to start with
        #  memory.
        self.vec_num = 0

        try:
            pinecone.whoami()
        except Exception as e:
            exit(1)

        if self.table_name not in pinecone.list_indexes():
            pinecone.create_index(
                self.table_name, dimension=dimension, metric=metric, pod_type=pod_type
            )
        self.index = pinecone.Index(self.table_name)

    def _add(self, vector: List, metadata: Dict) -> None:
        # no metadata here. We may wish to change that long term.
        id = str(self.vec_num)
        self.index.upsert([(id, vector, metadata)])
        self.vec_num += 1

    def clear(self) -> None:
        self.index.delete(deleteAll=True)

    def _get_relevant(self, vector: List, num_relevant: int) -> List[Any]:

        results = self.index.query(
            vector, top_k=num_relevant, include_metadata=True
        )
        return sorted(results.matches, key=lambda x: x.score)

    def get_stats(self):
        return self.index.describe_index_stats()
