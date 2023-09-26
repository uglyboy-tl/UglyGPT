#!/usr/bin/env python3
# -*-coding:utf-8-*-

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, List

DEFAULT_N = 10

class Index(ABC):
    defaule_n: int = DEFAULT_N

    @abstractmethod
    def search(self, query: str, n: int) -> List[str]:
        pass

    def get(self, query: str) -> str:
        try:
            return self.search(query, 1)[0]
        except:
            return ""

@dataclass
class Memory(Index, ABC):

    @abstractmethod
    def add(self, chat: Tuple[str, str]):
        pass