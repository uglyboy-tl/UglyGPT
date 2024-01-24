#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from typing import Optional, Dict, List, TypeVar, Generic

from pydantic import BaseModel

from core import MapChain
from .base import Action
from workflows.utils.sqlite import KVCache

ResponseModel = TypeVar("ResponseModel", bound=BaseModel)

@dataclass
class MapSqlite(Action, Generic[ResponseModel]):
    map_keys: Optional[list] = None
    table: Optional[str] = None

    def __post_init__(self):
        if self.map_keys is not None:
            self.llm = MapChain[ResponseModel](self.prompt, self.model, self.role, self.response_model, map_keys=self.map_keys)
        else:
            self.llm = MapChain[ResponseModel](self.prompt, self.model, self.role, self.response_model)

        self._reset_cache()
        return super().__post_init__()

    def ask(self, *args, **kwargs) -> List[str|BaseModel]:
        response = self.llm(*args, **kwargs)
        return response

    def _save(self, data: Optional[Dict[str,str|BaseModel]] = None, filename: Optional[str] = None):
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