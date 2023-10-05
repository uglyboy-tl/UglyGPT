#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
import sqlite3

from .bm25 import BM25DB

@dataclass
class BM25SQLite(BM25DB):
    table_prefix: str = 'bm25'

    def __post_init__(self):
        self._conn = sqlite3.connect(self.path)
        super().__post_init__()

    def _create_table(self) -> None:
        pass

    async def _save(self) -> None:
        pass

    def _load(self) -> None:
        pass