#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable
from loguru import logger

from .llm import LLM


@dataclass
class ReduceChain(LLM):
    reduce_keys: List[str] = field(default_factory=lambda: ["input"])
    format: Callable[[str], str] = field(default_factory=lambda: lambda x: x)

    def _validate_inputs(self, inputs: Dict[str, Any]) -> None:
        self.num = len(inputs[self.reduce_keys[0]])
        for reduce_key in self.reduce_keys:
            self._validate_reduce_key(reduce_key, inputs)
        assert "history" in self.input_keys, f"ReduceChain expects history to be in input_keys"
        if not hasattr(inputs, "history"):
            inputs["history"] = ""
        super()._validate_inputs(inputs)

    def _validate_reduce_key(self, reduce_key: str, inputs: Dict[str, Any]) -> None:
        assert reduce_key in self.input_keys, f"ReduceChain expects {reduce_key} to be in input_keys"
        assert isinstance(inputs[reduce_key], List), f"ReduceChain expects {reduce_key} to be a list of strings"
        assert len(inputs[reduce_key]) == self.num, f"ReduceChain expects {reduce_key} to be a list of strings with the same length"

    def _call(self, inputs: Dict[str, Any]) -> str:
        result = inputs["history"]
        for i in range(self.num):
            result = self._process_input(i, inputs, result)
            logger.debug(f"ReduceChain: {i} finished")
            logger.debug(f"ReduceChain: {result}")
        return result

    def _process_input(self, index: int, inputs: Dict[str, Any], history: str) -> str:
        new_input = inputs.copy()
        if index > 0:
            new_input.pop("history")
            new_input["history"] = self.format(history)
        new_input.update({reduce_key: inputs[reduce_key][index] for reduce_key in self.reduce_keys})
        return super()._call(new_input)