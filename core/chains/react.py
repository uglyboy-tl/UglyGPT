#!/usr/bin/env python3
# -*-coding:utf-8-*-

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Type, List, Optional

from loguru import logger

from core.llm import BaseLanguageModel
from .llm import LLM


@dataclass
class ReAct(ABC):
    thought: Optional[str] = None
    action: Optional[str] = None
    params: Optional[Dict[str, str]] = None
    current: bool = True

    def __post_init__(self):
        self.obs = self.run()

    @abstractmethod
    def run(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def parse(cls, text: str, llm: BaseLanguageModel ) -> "ReAct":
        pass

    @property
    @abstractmethod
    def done(self) -> bool:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    def info(self) -> str:
        if self.done:
            return f"[Thought]: {self.thought}"
        else:
            return f"[Thought]: {self.thought}\n[Action]: {self.action}\n[Params]: {self.params}\n[Obs]: {self.obs}"


@dataclass
class ReActChain(LLM):
    cls: Optional[Type[ReAct]] = None

    def __post_init__(self):
        self._acts = []
        super().__post_init__()

    @property
    def input_keys(self) -> List[str]:
        return ["prompt"]

    def _process(self, act: ReAct) -> str:
        logger.success(act.info)
        while not act.done:
            if self._acts:
                self._acts[-1].current = False
            self._acts.append(act)
            inputs = {"prompt": "\n".join(str(a) for a in self._acts)}
            response = self._call(inputs)
            act = self.cls.parse(response, self.llm)  # type: ignore
            logger.success(act.info)
        return act.info

    def __call__(self, act: Optional[ReAct] = None) -> str:
        if act is None:
            inputs = {"prompt": "Start!"}
            inputs = self._prep_inputs(inputs)
            response = self._call(inputs)
            act = self.cls.parse(response, self.llm)  # type: ignore
        return self._process(act)
