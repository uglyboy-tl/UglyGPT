"""Base class for memory providers."""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List

from uglygpt.base import AbstractSingleton
from uglygpt.provider import EmbeddingProvider


@dataclass
class BaseIndex(AbstractSingleton):
    embeddings: EmbeddingProvider
    vec_num = 0

    def add(self, text: str, metadata: Dict = None) -> None:
        """Adds to memory"""
        vector = self.embeddings.embedding(text)
        if metadata is None:
            metadata = {"raw_text": text}
        else:
            metadata["raw_text"] = text
        self._add(vector, metadata)

    def get(self, text: str) -> List[Any] | None:
        return self.get_relevant(text, key="raw_text")

    def get_relevant(self, text: str, num_relevant: int = 5, key=None) -> List[Any] | None:
        """Gets relevant memory for"""
        vector = self.embeddings.embedding(text)
        results = self._get_relevant(vector, num_relevant)
        if key is None:
            return results
        return [str(item["metadata"][key]) for item in results]

    @abc.abstractmethod
    def _add(self, vector: List, metadata: Dict) -> None:
        """Adds to memory"""
        pass

    @abc.abstractmethod
    def clear(self) -> None:
        """Clears memory"""
        pass

    @abc.abstractmethod
    def _get_relevant(self, vector: List, num_relevant: int = 5) -> List[Any] | None:
        """Gets relevant memory for"""
        pass

    @abc.abstractmethod
    def get_stats(self):
        """Get stats from memory"""
        pass
