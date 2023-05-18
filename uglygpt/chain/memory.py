import abc
from typing import Any, Dict, List

class BaseMemory(abc.ABC):
    """Base interface for memory in chains."""

    @property
    @abc.abstractmethod
    def memory_variables(self) -> List[str]:
        """Input keys this memory class will load dynamically."""

    @abc.abstractmethod
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return key-value pairs given the text input to the chain.

        If None, return all memories
        """

    @abc.abstractmethod
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save the context of this model run to memory."""

    @abc.abstractmethod
    def clear(self) -> None:
        """Clear memory contents."""
