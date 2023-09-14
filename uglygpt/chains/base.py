#!/usr/bin/env python3
# -*-coding:utf-8-*-

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Union


@dataclass
class Chain(ABC):
    """Chain 的基类，定义了 Chain 的基本结构。
    Chain 的主要作用是规范化输入输出，以及规范化输入的格式
    另外就是对调用 LLM 的参数做预处理，例如对输入的文本进行 Prompt 的拼接和补充，对过长的文本进行切割等
    """

    @property
    @abstractmethod
    def input_keys(self) -> List[str]:
        """Input keys this chain expects."""

    def _validate_inputs(self, inputs: Dict[str, Any]) -> None:
        """Check that all inputs are present."""
        missing_keys = set(self.input_keys).difference(inputs)
        if missing_keys:
            raise ValueError(f"Missing some input keys: {missing_keys}")

    def prep_inputs(self, inputs: Union[Dict[str, Any], Any]) -> Dict[str, str]:
        """Validate and prep inputs."""
        if not isinstance(inputs, dict):
            _input_keys = set(self.input_keys)
            if len(_input_keys) != 1:
                raise ValueError(
                    f"A single string input was passed in, but this chain expects "
                    f"multiple inputs ({_input_keys}). When a chain expects "
                    f"multiple inputs, please call it by passing in a dictionary, "
                    "eg `chain({'foo': 1, 'bar': 2})`"
                )
            inputs = {list(_input_keys)[0]: inputs}
        self._validate_inputs(inputs)
        return inputs

    @abstractmethod
    def _call(self, inputs: Dict[str, Any]) -> str:
        """Execute the chain."""

    def _run(self, inputs: Dict[str, Any]) -> str:
        """Execute the chain."""
        inputs = self.prep_inputs(inputs)
        try:
            outputs = self._call(inputs)
        except (KeyboardInterrupt, Exception) as e:
            raise e
        return outputs

    def __call__(self, *args: Any, **kwargs: Any) -> str:
        """Run the chain as text in, text out or multiple variables, text out."""
        if args and not kwargs:
            if len(args) != 1:
                raise ValueError(
                    "`run` supports only one positional argument.")
            return self._run(args[0])

        if kwargs and not args:
            return self._run(kwargs)

        if not kwargs and not args:
            return self._run({})

        raise ValueError(
            f"`run` supported with either positional arguments or keyword arguments"
            f" but not both. Got args: {args} and kwargs: {kwargs}."
        )
