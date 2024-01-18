#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from typing import Optional, Dict, List
import json

from uglygpt.chains import MapChain
from .base import Action
from workflows.utils.sqlite import KVCache

@dataclass
class MapSqlite(Action):
    map_keys: Optional[list] = None
    table: Optional[str] = None

    def __post_init__(self):
        if self.map_keys is not None:
            self.llm = MapChain(self.prompt, self.llm_name, map_keys=self.map_keys)
        else:
            self.llm = MapChain(self.prompt, self.llm_name)

        self._reset_cache()
        return super().__post_init__()

    def ask(self, *args, **kwargs) -> List[str]:
        response = self.llm(*args, **kwargs)
        json_response = json.loads(response)
        return json_response

    def _save(self, data: Optional[Dict[str,str]] = None, filename: Optional[str] = None):
        if filename:
            self._reset_cache(filename)
        if not data:
            return
        self.cache.set(data)

    def _load(self, keys: Optional[List[str]] = None, filename: Optional[str] = None):
        if filename:
            self._reset_cache(filename)
        return self.cache.get(keys)

    def _reset_cache(self, filename: Optional[str] = None):
        if filename:
            self.filename = filename

        if self.table is None:
            table = self.__class__.__name__
        else:
            table = self.table

        if self.filename is None:
            self.cache = KVCache(table=table)
        else:
            self.cache = KVCache(self.filename, table)