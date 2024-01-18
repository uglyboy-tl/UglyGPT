#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import Tuple, List

from agent.indexes import DB, BM25DB

SEPARATOR = '\u001f'

@dataclass
class Memory:
    input_db: str|DB

    def __post_init__(self):
        if isinstance(self.input_db, str):
            self._db = BM25DB(self.input_db)
        elif isinstance(self.input_db, DB):
            self._db = self.input_db

    def update(self, chat: Tuple[str, str]):
        if self._db is not None:
            self._db.add(SEPARATOR.join(chat))

    def get_memory(self, query: str, n: int = DB.default_n) -> List[Tuple[str, str]]:
        texts = self._db.search(query, n) if self._db is not None else []
        chats = []
        for text in texts:
            chat = text.split(SEPARATOR)
            assert len(chat) == 2
            chats.append((chat[0], chat[1]))
        return chats