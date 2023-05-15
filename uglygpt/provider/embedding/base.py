"""Base Class for Embedding Providers"""
import abc
from uglygpt.base import AbstractSingleton

class EmbeddingProvider(AbstractSingleton):
    @abc.abstractmethod
    def embedding(self, texts:str) -> list:
        pass