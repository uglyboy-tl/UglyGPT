#!/usr/bin/env python3
# -*-coding:utf-8-*-

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List

DEFAULT_N = 5

class Index(ABC):
    default_n: int = DEFAULT_N

    @abstractmethod
    def search(self, query: str, n: int) -> List[str]:
        pass

    def get(self, query: str) -> str:
        try:
            return self.search(query, 1)[0]
        except:
            return ""

@dataclass
class DB(Index, ABC):
    path: str

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def add(self, text: str, metadata: Dict[str, str]):
        pass