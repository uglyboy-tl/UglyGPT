#!/usr/bin/env python3
#-*-coding:utf-8-*-

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Union

@dataclass
class Chain(ABC):
    """Base interface that all chains should implement."""

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

    def __call__(self, inputs: Dict[str, Any]) -> str:
        """Execute the chain."""
        inputs = self.prep_inputs(inputs)
        try:
            outputs = self._call(inputs)
        except (KeyboardInterrupt, Exception) as e:
            raise e
        return outputs