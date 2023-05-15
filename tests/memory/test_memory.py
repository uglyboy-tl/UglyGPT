import random
import string
import pytest

from uglygpt.memory import get_memory
from uglygpt.base.config import config

def test_get_pinecone():
    config.set_memory_backend("pinecone")
    memory1 = get_memory(config)
    config.set_memory_backend("local")
    memory2 = get_memory(config)
    assert id(memory1) == id(memory2)

@pytest.mark.parametrize("memory_backend", ["local", "no_memory","pinecone"])
def test_get_memory(memory_backend):
    config.set_memory_backend(memory_backend)
    assert id(get_memory(config)) == id(get_memory(config))


@pytest.fixture(params = ["local", "pinecone"])
def memory(request):
    config.set_memory_backend(request.param)
    return get_memory(config)

def generate_random_string(length):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))

def test_get_relevant(memory):
    memory.clear()
    # Add example texts to the cache
    example_texts = [
        "The quick brown fox jumps over the lazy dog",
        "I love machine learning and natural language processing",
        "The cake is a lie, but the pie is always true",
        "ChatGPT is an advanced AI model for conversation",
    ]
    for text in example_texts:
        memory.add(text)

    # Add some random strings to test noise
    for _ in range(5):
        memory.add(generate_random_string(10))
    """Test getting relevant texts from the cache."""
    query = "I'm interested in artificial intelligence and NLP"
    k = 3
    relevant_texts = memory.get_relevant(query, k)

    print(f"Top {k} relevant texts for the query '{query}':")
    for i, text in enumerate(relevant_texts, start=1):
        print(f"{i}. {text}")

    assert len(relevant_texts) == k
    assert example_texts[1] in relevant_texts


def test_get(memory):
    memory.clear()
    assert memory.get("test") == []

    memory.add("test")
    assert memory.get("test") == ["test"]


@pytest.mark.vcr
def test_get_relevant2(memory) -> None:
    memory.clear()
    text1 = "Sample text 1"
    text2 = "Sample text 2"
    memory.add(text1)
    memory.add(text2)

    result = memory.get_relevant(text1, 1)
    assert result == [text1]
