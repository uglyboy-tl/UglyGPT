from uglygpt.provider.embedding.base import EmbeddingProvider
from uglygpt.base import logger

supported_embedding_provider = []

try:
    from uglygpt.provider.embedding.openai import OpenAIEmbedding
    supported_embedding_provider.append(OpenAIEmbedding)
except ImportError:
    print("OpenAIEmbeddings not installed. Skipping import.")
    OpenAIEmbeddings = None

def get_embedding_provider(embedding_provider_name: str = "openai") -> EmbeddingProvider:
    """
    Get the embedding provider.

    Args:
        embedding_provider_name: str

    Returns: EmbeddingProvider
    """
    if embedding_provider_name == "openai":
        if not OpenAIEmbedding:
            logger.error(
                "Error: OpenAIEmbedding is not installed. Please install openai"
                " to use OpenAI as a Embedding provider."
            )
        else:
            return OpenAIEmbedding()
    elif embedding_provider_name == "google":
        return None
    else:
        logger.error("Embedding provider not implemented")
        return None

def get_embedding_vector(text: str) -> list:
    """
    Get the embedding vector for a given text.

    Args:
        text: str

    Returns: list
    """
    embedding_provider = get_embedding_provider()
    if embedding_provider is None:
        raise NotImplementedError("Embedding provider not implemented")
    return embedding_provider.embedding(text)