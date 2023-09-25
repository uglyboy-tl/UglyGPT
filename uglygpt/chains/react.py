from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Type, List, Optional
from .llm import LLMChain
from loguru import logger

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
    def parse(cls, text: str) -> "ReAct":
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
class ReActChain(LLMChain):
    cls: Optional[Type[ReAct]] = None

    def __post_init__(self):
        self._acts = []
        super().__post_init__()

    @property
    def input_keys(self) -> List[str]:
        return ["prompt"]

    def __call__(self, act: Optional[ReAct] = None) -> str:
        if act is None:
            resopnse = self._check_and_call({"prompt": ""})
            act = self.cls.parse(resopnse) # type: ignore
        logger.success(act.info)
        while act.done == False:
            if len(self._acts) > 0:
                self._acts[-1].current = False
            self._acts.append(act)
            history = "\n".join([str(act) for act in self._acts])
            resopnse = self._check_and_call({"prompt": history})
            act = self.cls.parse(resopnse)  # type: ignore
            logger.success(act.info)
        return act.info