from dataclasses import dataclass
from typing import List, Dict, Any
from .base import Chain


@dataclass
class SimpleChain(Chain):
    input_key: str = "input"

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    def _call(self, inputs: Dict[str, Any]) -> str:
        return inputs[self.input_key]