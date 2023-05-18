from uglygpt.base import logger
from uglygpt.indexes.local import LocalIndex
from uglygpt.indexes.no_index import NoIndex
from uglygpt.indexes.base import BaseIndex

# List of supported memory backends
# Add a backend to this list if the import attempt is successful
supported_memory = ["local", "no_memory"]

try:
    from uglygpt.indexes.pinecone import PineconeIndex

    supported_memory.append("pinecone")
except ImportError:
    logger.warn("Pinecone not installed. Skipping import.")
    PineconeIndex = None


def get_memory(cfg, init=False):
    memory = None
    if cfg.memory_backend == "pinecone":
        if not PineconeIndex:
            logger.warn(
                "Error: Pinecone is not installed. Please install pinecone"
                " to use Pinecone as a memory backend."
            )
        else:
            memory = PineconeIndex(cfg)
            if init:
                memory.clear()
    elif cfg.memory_backend == "no_memory":
        memory = NoIndex(cfg)

    if memory is None:
        memory = LocalIndex(cfg)
        if init:
            memory.clear()
    return memory

__all__ = ["get_memory", "BaseIndex"]