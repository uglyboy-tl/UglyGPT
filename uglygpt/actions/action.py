#!/usr/bin/env python3
# -*-coding:utf-8-*-

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing import Optional

from uglygpt.chains import LLMChain
from uglygpt.base import File


@dataclass
class Action(ABC):
    role: Optional[str | None] = None
    filename: Optional[str | None] = None
    llm: LLMChain = field(default_factory=LLMChain)

    def __post_init__(self):
        if self.role:
            self.llm.llm.set_system(self.role)

    def ask(self, *args, **kwargs) -> str:
        response = self.llm(*args, **kwargs)
        return response

    def _save(self, data=None, filename=None):
        if not filename:
            if self.filename:
                filename = self.filename
            else:
                return
        if not data:
            raise ValueError("data is required")
        File.save(filename, data)

    def _load(self, filename=None):
        if not filename:
            if self.filename:
                filename = self.filename
            else:
                raise ValueError("filename is required")
        data = File.load(filename)
        return data

    def _parse(self, text: str):
        return text

    @abstractmethod
    def run(self, *args, **kwargs):
        pass
