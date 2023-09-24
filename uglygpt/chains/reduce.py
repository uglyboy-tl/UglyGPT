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
    reduce_key: str = "input"
    separator: str = "\n"
    check_func: Optional[Callable[[str], bool]] = None # 默认不分组进行reduce，如果需要分组（大概率是因为字数限制），需要传入一个函数，根据字符串返回True/False

    @property
    def input_keys(self) -> List[str]:
        return self.chain.input_keys

    def _validate_inputs(self, inputs: Dict[str, Any]) -> None:
        if self.reduce_key not in self.input_keys:
            raise ValueError(
                f"MapChain expects {self.reduce_key} to be in input_keys")
        if self.check_func is not None:
            if "history" not in self.input_keys:
                raise ValueError(
                    f"MapChain expects history to be in input_keys")
            inputs["history"] = ""
        super()._validate_inputs(inputs)
        if not isinstance(inputs[self.reduce_key], List):
            raise ValueError(
                f"MapChain expects {self.reduce_key} to be a list of strings")

    def _call(self, inputs: Dict[str, Any]) -> str:
        # combine the inputs
        text_list = []
        text = ""
        for item in inputs[self.reduce_key]:
            if self._is_too_long(text + self.separator + item):
                text_list.append(text)
                text = item
            else:
                text +=  self.separator + item if text!= "" else item
        text_list.append(text)
        #logger.debug(f"text_list: {text_list}")

        result = ""
        for text in text_list:
            new_input: Dict = {k: v for k, v in inputs.items() if k != self.reduce_key}
            new_input["history"] = result
            new_input[self.reduce_key] = text
            #logger.debug(f"new_input: {new_input}")
            result = self.chain(**new_input)
            logger.debug(f"result: {result}")
        return result

    def _is_too_long(self, text: str) -> bool:
        if self.check_func is None:
            self.check_func = lambda x: False
        return True if self.check_func(text) else False
