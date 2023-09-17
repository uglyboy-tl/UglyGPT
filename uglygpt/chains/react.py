from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Type, List
from .llm import LLMChain
from loguru import logger

@dataclass
class ReAct(ABC):
    thought: str
    action: str
    params: Dict[str, str]
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

@dataclass
class ReActChain(LLMChain):
    prompt_template: str = "{history}"
    cls: Type[ReAct]|None = None

    def __post_init__(self):
        self._acts = []
        super().__post_init__()

    @property
    def input_keys(self) -> List[str]:
        return ["history"]

    def __call__(self, act:ReAct|None = None) -> str:
        if act is None:
            resopnse = self._check_and_call({"history": ""})
            act = self.cls.parse(resopnse) # type: ignore
            logger.success(f"\n[Thought]:{act.thought}\n[Action]:{act.action}\n[Params]:{act.params}\n[Obs]:{act.obs}")
        while act.done == False:
            if len(self._acts) > 0:
                self._acts[-1].current = False
            self._acts.append(act)
            history = "\n".join([str(act) for act in self._acts])
            resopnse = self._check_and_call({"history": history})
            act = self.cls.parse(resopnse)  # type: ignore
            logger.success(f"\n[Thought]: {act.thought}\n[Action]: {act.action}\n[Params]: {act.params}\n[Obs]: {act.obs}")
        return act.thought