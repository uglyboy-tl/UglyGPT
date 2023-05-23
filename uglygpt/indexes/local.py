from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Dict

import numpy as np
import orjson

from uglygpt.indexes.base import BaseIndex
from uglygpt.provider import get_embedding_provider

EMBED_DIM = 1536
SAVE_OPTIONS = orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_SERIALIZE_DATACLASS


def create_default_embeddings():
    return np.zeros((0, EMBED_DIM)).astype(np.float32)


@dataclass
class CacheContent:
    embeddings: np.ndarray = field(
        default_factory=create_default_embeddings
    )
    metadata: List[Dict] = field(default_factory=list)

class LocalIndex(BaseIndex):
    """A class that stores the memory in a local file"""

    def __init__(self, cfg, memory_index: str = None) -> None:
        """Initialize a class instance

        Args:
            cfg: Config object

        Returns:
            None
        """
        self.embeddings = get_embedding_provider()
        workspace_path = Path(cfg.workspace_path)
        self.filename = workspace_path / f"{memory_index or cfg.memory_index}.json"

        self.filename.touch(exist_ok=True)

        with self.filename.open("rb") as f:
            file_content = f.read()

        self.data = CacheContent()

        if file_content != b"":
            data = orjson.loads(file_content)
            if data["embeddings"] != []:
                self.data.embeddings = np.array(data["embeddings"]).astype(np.float32)
            else:
                self.data.embeddings = create_default_embeddings()
            self.data.metadata = data["metadata"]

    def _add(self, vector: List, metadata: Dict) -> None:
        """
        Add text to our list of texts, add embedding as row to our
            embeddings-matrix

        Args:
            text: str

        Returns: None
        """
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

    def clear(self) -> None:
        """
        Clears the data in memory.

        Returns: A message indicating that the memory has been cleared.
        """
        self.data = CacheContent()
        with open(self.filename, "wb") as f:
            out = orjson.dumps(self.data, option=SAVE_OPTIONS)
            f.write(out)

    def _get_relevant(self, vector: List, num_relevant: int) -> list[Any]:
        """ "
        matrix-vector mult to find score-for-each-row-of-matrix
        get indices for top-k winning scores
        return texts for those indices
        Args:
            text: str
            k: int

        Returns: List[str]
        """

        scores = np.dot(self.data.embeddings, vector)

        top_k_indices = np.argsort(scores)[-num_relevant:][::-1]
        return [{"metadata":self.data.metadata[i]} for i in top_k_indices]

    def get_stats(self) -> tuple[int, tuple[int, ...]]:
        """
        Returns: The stats of the local cache.
        """
        return len(self.data.texts), self.data.embeddings.shape
