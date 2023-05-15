from uglygpt.provider import get_embedding_provider, get_llm_provider

def test_get_embedding_provider():
    assert id(get_embedding_provider()) == id(get_embedding_provider())
    assert id(get_embedding_provider()) != id(get_embedding_provider("google"))

def test_get_llm_provider():
    assert id(get_llm_provider()) == id(get_llm_provider())