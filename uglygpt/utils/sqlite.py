import sqlite3
from dataclasses import dataclass
from typing import Dict, List

from loguru import logger

from uglygpt.base import File


@dataclass
class KVCache:
    file: str = "resource/cache.db"
    table: str = "cache"
    expirationIntervalInDays: int = 10

    def __post_init__(self) -> None:
        path = File.to_path(self.file)
        with sqlite3.connect(path) as conn:
            cur = conn.cursor()
            cur.execute(
                f'CREATE TABLE IF NOT EXISTS {self.table} (key TEXT PRIMARY KEY, value TEXT, timestamp TEXT Not NULL DEFAULT (date(\'now\',\'localtime\')))')
        self._conn = sqlite3.connect(path)
        self._cur = self._conn.cursor()

    def get(self, keys: List[str] | str | None) -> Dict[str, str]:
        if keys is None:
            self._cur.execute(
                f"SELECT key, value FROM {self.table} WHERE date('now', 'localtime') < date(timestamp, '+? day')", (self.expirationIntervalInDays,))
            return {row[0]: row[1] for row in self._cur.fetchall()}
        if isinstance(keys, str):
            keys = [keys]

        placeholders = ', '.join('?' for _ in keys)
        params = keys + [str(self.expirationIntervalInDays)]
        self._cur.execute(
            f"SELECT key, value FROM {self.table} WHERE key IN ({placeholders}) and date('now', 'localtime') < date(timestamp, '+' || ? || ' day')", params)

        return {row[0]: row[1] for row in self._cur.fetchall()}

    def set(self, data: Dict[str, str]):
        self._cur.executemany(f'''
            INSERT OR REPLACE INTO {self.table} (key, value)
            VALUES (?, ?)
        ''', data.items())
        self._conn.commit()
