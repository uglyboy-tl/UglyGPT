import pinecone

from uglygpt.memory.base import MemoryProviderSingleton
from uglygpt.provider import get_embedding_vector

class Pinecone:
    def __init__(self, cfg, memory_index = None):
        pinecone_api_key = cfg.pinecone_api_key
        pinecone_region = cfg.pinecone_region
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_region)

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

    def add(self, data, metadata=None, id=None):
        # no metadata here. We may wish to change that long term.
        vector = get_embedding_vector(data)
        if metadata is None:
            metadata = {"raw_text": data}
        if id is None:
            id = str(self.vec_num)
        self.index.upsert([(id, vector, metadata)])
        _text = f"Inserting data into memory at index: {self.vec_num}:\n data: {data}"
        self.vec_num += 1
        return _text

    def get(self, data):
        return self.get_relevant(data)

    def clear(self):
        self.index.delete(deleteAll=True)
        return "Obliviated"

    def get_relevant(self, data, num_relevant=5, key="raw_text"):
        """
        Returns all the data in the memory that is relevant to the given data.
        :param data: The data to compare to.
        :param num_relevant: The number of relevant data to return. Defaults to 5
        """
        vector = get_embedding_vector(data)
        results = self.index.query(
            vector, top_k=num_relevant, include_metadata=True
        )
        sorted_results = sorted(results.matches, key=lambda x: x.score)
        return [str(item["metadata"][key]) for item in sorted_results]

    def get_stats(self):
        return self.index.describe_index_stats()

class PineconeMemory(Pinecone, MemoryProviderSingleton):
    pass