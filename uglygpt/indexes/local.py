from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, List, Dict

import numpy as np
import orjson

from uglygpt.indexes.base import BaseIndex
from uglygpt.provider import get_embedding_vector

EMBED_DIM = 1536
SAVE_OPTIONS = orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS


def create_default_embeddings():
    return np.zeros((0, EMBED_DIM)).astype(np.float32)


@dataclasses.dataclass
class CacheContent:
    id: List[str] = dataclasses.field(default_factory=list)
    texts: List[str] = dataclasses.field(default_factory=list)
    embeddings: np.ndarray = dataclasses.field(
        default_factory=create_default_embeddings
    )
    metadata: List[Dict] = dataclasses.field(default_factory=list)


class LocalCache:
    """A class that stores the memory in a local file"""

    def __init__(self, cfg, memory_index: str = None) -> None:
        """Initialize a class instance

        Args:
            cfg: Config object

        Returns:
            None
        """
        workspace_path = Path(cfg.workspace_path)
        self.filename = workspace_path / f"{memory_index or cfg.memory_index}.json"

        self.filename.touch(exist_ok=True)

        with self.filename.open("rb") as f:
            file_content = f.read()

        self.data = CacheContent()

        if file_content != b"":
            data = orjson.loads(file_content)
            self.data.id = data["id"]
            self.data.texts = data["texts"]
            if data["embeddings"] != []:
                self.data.embeddings = np.array(data["embeddings"]).astype(np.float32)
            else:
                self.data.embeddings = create_default_embeddings()
            self.data.metadata = data["metadata"]

    def add(self, text: str, metadata: dict = None, id: str = None) -> str:
        """
        Add text to our list of texts, add embedding as row to our
            embeddings-matrix

        Args:
            text: str

        Returns: None
        """
        if "Command Error:" in text:
            return ""
        if metadata is None:
            metadata = {}
        if id is None:
            id = len(self.data.metadata) + 1
        self.data.id.append(id)
        self.data.texts.append(text)
        vector = get_embedding_vector(text)
        vector = np.array(vector).astype(np.float32)
        vector = vector[np.newaxis, :]
        self.data.embeddings = np.concatenate(
            [
                self.data.embeddings,
                vector,
            ],
            axis=0,
        )
        self.data.metadata.append(metadata)

        with open(self.filename, "wb") as f:
            out = orjson.dumps(self.data, option=SAVE_OPTIONS)
            f.write(out)
        return text

    def clear(self) -> str:
        """
        Clears the data in memory.

        Returns: A message indicating that the memory has been cleared.
        """
        self.data = CacheContent()
        with open(self.filename, "wb") as f:
            out = orjson.dumps(self.data, option=SAVE_OPTIONS)
            f.write(out)
        return "Obliviated"

    def get(self, vector: list) -> list[Any] | None:
        """
        Gets the data from the memory that is most relevant to the given data.

        Args:
            data: The data to compare to.

        Returns: The most relevant data.
        """
        return self.get_relevant(vector, 5)

    def get_relevant(self, query: str, num_relevant: int, key:str = None) -> list[Any]:
        """ "
        matrix-vector mult to find score-for-each-row-of-matrix
        get indices for top-k winning scores
        return texts for those indices
        Args:
            text: str
            k: int

        Returns: List[str]
        """
        vector = get_embedding_vector(query)
        scores = np.dot(self.data.embeddings, vector)

        top_k_indices = np.argsort(scores)[-num_relevant:][::-1]
        if key:
            return [self.data.metadata[i][key] for i in top_k_indices]
        else:
            return [self.data.texts[i] for i in top_k_indices]

    def get_stats(self) -> tuple[int, tuple[int, ...]]:
        """
        Returns: The stats of the local cache.
        """
        return len(self.data.texts), self.data.embeddings.shape

class LocalIndex(LocalCache, BaseIndex):
    pass
