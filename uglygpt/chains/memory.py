#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Tuple, List


@dataclass
class Memory(ABC):

    @abstractmethod
    def add(self, chat: Tuple[str, str]):
        pass

    @abstractmethod
    def get_top(self, query: str, n: int) -> List[str]:
        pass

    def get(self, query: str) -> str:
        try:
            return self.get_top(query, 1)[0]
        except:
            return ""
