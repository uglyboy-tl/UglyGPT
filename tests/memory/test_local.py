# sourcery skip: snake-case-functions
"""Tests for LocalCache class"""
import orjson
from pathlib import Path

import pytest
from pytest_mock import MockerFixture


from uglygpt.memory.local import EMBED_DIM, SAVE_OPTIONS
from uglygpt.memory.local import LocalMemory as LocalCache_
from uglygpt.base.config import Config


@pytest.fixture()
def workspace():
    cfg = Config()
    return Path(cfg.workspace_path) / "Test"

@pytest.fixture()
def config(mocker: MockerFixture, workspace) -> Config:
    config = Config()

    # Do a little setup and teardown since the config object is a singleton
    mocker.patch.multiple(
        config,
        workspace_path = workspace,
        file_logger_path = workspace / f"file_logger.txt",
    )
    yield config

@pytest.fixture
def LocalCache():
    # Hack, real gross. Singletons are not good times.
    if LocalCache_ in LocalCache_._instances:
        del LocalCache_._instances[LocalCache_]
    return LocalCache_


@pytest.fixture
def mock_embed_with_ada(mocker: MockerFixture):
    mocker.patch(
        "uglygpt.provider.get_embedding_vector",
        return_value=[0.1] * EMBED_DIM,
    )


def test_init_without_backing_file(LocalCache, config, workspace):
    cache_file = workspace / f"{config.memory_index}.json"
    cache_file.unlink(missing_ok=True)

    LocalCache(config)
    assert cache_file.exists()
    assert cache_file.read_text() == ""


def test_init_with_backing_empty_file(LocalCache, config, workspace):
    cache_file = workspace / f"{config.memory_index}.json"
    cache_file.touch()

    assert cache_file.exists()
    LocalCache(config)
    assert cache_file.exists()
    assert cache_file.read_text() == ""


def test_init_with_backing_file(LocalCache, config, workspace):
    cache_file = workspace / f"{config.memory_index}.json"
    cache_file.touch()

    raw_data = {"id":[],"texts":["test"],"embeddings":[],"metadata":[]}
    data = orjson.dumps(raw_data, option=SAVE_OPTIONS)
    with cache_file.open("wb") as f:
        f.write(data)

    assert cache_file.exists()
    memory = LocalCache(config)
    assert cache_file.exists()
    assert "test" in memory.data.texts


def test_add(LocalCache, config, mock_embed_with_ada):
    cache = LocalCache(config)
    cache.clear()
    cache.add("test")
    assert cache.data.texts == ["test"]
    assert cache.data.embeddings.shape == (1, EMBED_DIM)


def test_clear(LocalCache, config, mock_embed_with_ada):
    cache = LocalCache(config)
    cache.clear()
    assert cache.data.texts == []
    assert cache.data.embeddings.shape == (0, EMBED_DIM)

    cache.add("test")
    assert cache.data.texts == ["test"]
    assert cache.data.embeddings.shape == (1, EMBED_DIM)

    cache.clear()
    assert cache.data.texts == []
    assert cache.data.embeddings.shape == (0, EMBED_DIM)

def test_get_stats(LocalCache, config, mock_embed_with_ada) -> None:
    cache = LocalCache(config)
    cache.clear()
    text = "Sample text"
    cache.add(text)
    stats = cache.get_stats()
    assert stats == (1, cache.data.embeddings.shape)