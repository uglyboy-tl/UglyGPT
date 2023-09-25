#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable, Optional
from loguru import logger

from .base import Chain
from .llm import LLMChain


@dataclass
class ReduceChain(Chain):
    chain: Chain = field(default_factory=LLMChain)
    reduce_keys: List[str] = field(default_factory=lambda: ["input"])
    format: Callable[[str], str] = field(default_factory=lambda: lambda x: x)

    @property
    def input_keys(self) -> List[str]:
        return self.chain.input_keys

    def _validate_inputs(self, inputs: Dict[str, Any]) -> None:
        self.num = len(inputs[self.reduce_keys[0]])
        for reduce_key in self.reduce_keys:
            assert reduce_key in self.input_keys, f"MapChain expects {reduce_key} to be in input_keys"
            assert isinstance(inputs[reduce_key], List), f"MapChain expects {reduce_key} to be a list of strings"
            assert len(inputs[reduce_key]) == self.num, f"MapChain expects {reduce_key} to be a list of strings with the same length"
        assert "history" in self.input_keys, f"MapChain expects history to be in input_keys"
        inputs["history"] = ""
        super()._validate_inputs(inputs)

    def _call(self, inputs: Dict[str, Any]) -> str:
        result = ""
        for i in range(self.num):
            new_input: Dict = {k: v for k, v in inputs.items() if k not in self.reduce_keys}
            new_input["history"] = self.format(result)
            for reduce_key in self.reduce_keys:
                new_input[reduce_key] = inputs[reduce_key][i]
            result = self.chain(**new_input)
            logger.debug(f"result: {result}")
        return result
