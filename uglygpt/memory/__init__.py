from uglygpt.base import logger
from uglygpt.memory.local import LocalMemory
from uglygpt.memory.no_memory import NoMemory

# List of supported memory backends
# Add a backend to this list if the import attempt is successful
supported_memory = ["local", "no_memory"]

try:
    from uglygpt.memory.pinecone import PineconeMemory

    supported_memory.append("pinecone")
except ImportError:
    PineconeMemory = None


def get_memory(cfg, init=False):
    memory = None
    if cfg.memory_backend == "pinecone":
        if not PineconeMemory:
            logger.warn(
                "Error: Pinecone is not installed. Please install pinecone"
                " to use Pinecone as a memory backend."
            )
        else:
            memory = PineconeMemory(cfg)
            if init:
                memory.clear()
    elif cfg.memory_backend == "no_memory":
        memory = NoMemory(cfg)

    if memory is None:
        memory = LocalMemory(cfg)
        if init:
            memory.clear()
    return memory