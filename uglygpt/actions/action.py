#!/usr/bin/env python3
#-*-coding:utf-8-*-

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from uglygpt.chains import LLMChain
from uglygpt.base import File

@dataclass
class Action(ABC):
    role: str = None
    filename: str = None
    llm: LLMChain = field(default_factory=LLMChain)

    def __post_init__(self):
        if self.role:
            self.llm.llm.set_system(self.role)

    def _ask(self, *args, **kwargs) -> str:
        response = self.llm(*args, **kwargs)
        return response

    def _save(self, filename=None, data=None):
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

    def _parse(self, result: str):
        return result

    @abstractmethod
    def run(self, *args, **kwargs):
        pass