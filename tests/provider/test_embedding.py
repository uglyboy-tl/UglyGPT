import pytest
from uglygpt.provider import get_embedding_provider

@pytest.mark.parametrize("embedding_provider", ["openai"])
def test_get_embedding_provider(embedding_provider):
    embedding = get_embedding_provider(embedding_provider)
    assert len(embedding.embedding("test")) == 1536
