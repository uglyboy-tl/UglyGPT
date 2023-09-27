#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from typing import Tuple, List

from uglygpt.indexes import DB

@dataclass
class Memory:
    db: DB
    short_term_memory: str = ""

    def update(self, chat: Tuple[str, str]):
        if self.db is not None:
            self.db.add(chat)

    def get_long_term_memory(self, query: str, n: int = DB.default_n) -> List[str]:
        return self.db.search(query, n) if self.db is not None else []