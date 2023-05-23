"""A class that does not store any data. This is the default memory provider."""
from __future__ import annotations

from typing import Any, List, Dict

from uglygpt.indexes.base import BaseIndex

class NoIndex(BaseIndex):
    """
    A class that does not store any data. This is the default memory provider.
    """

    def __init__(self, cfg):
        """
        Initializes the NoMemory provider.

        Args:
            cfg: The config object.

        Returns: None
        """
        pass

    def add(self, text: str, metadata: Dict = None) -> None:
        pass

    def _add(self, vector: List, metadata: Dict) -> None:
        """
        Adds a data point to the memory. No action is taken in NoMemory.

        Args:
            data: The data to add.

        Returns: An empty string.
        """
        return None

    def clear(self) -> None:
        """
        Clears the memory. No action is taken in NoMemory.

        Returns: An empty string.
        """
    def get(self, text: str) -> List[Any] | None:
        return None

    def get_relevant(self, text: str, num_relevant: int = 5, key=None) -> List[Any] | None:
        return None

    def _get_relevant(self, vector: str, num_relevant: int = 5) -> list[Any] | None:
        """
        Returns all the data in the memory that is relevant to the given data.
        NoMemory always returns None.

        Args:
            data: The data to compare to.
            num_relevant: The number of relevant data to return.

        Returns: None
        """
        return None

    def get_stats(self):
        """
        Returns: An empty dictionary as there are no stats in NoMemory.
        """
        return {}
