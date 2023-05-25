from __future__ import annotations
import abc
from dataclasses import dataclass
from typing import Any, Dict, List, Union, Optional

from uglygpt.chains.memory import BaseMemory

@dataclass
class Chain(abc.ABC):
    """Base interface that all chains should implement."""
    memory: Optional[BaseMemory] = None

    @property
    @abc.abstractmethod
    def input_keys(self) -> List[str]:
        """Input keys this chain expects."""

    @property
    @abc.abstractmethod
    def output_keys(self) -> List[str]:
        """Output keys this chain expects."""

    def _validate_inputs(self, inputs: Dict[str, Any]) -> None:
        """Check that all inputs are present."""
        missing_keys = set(self.input_keys).difference(inputs)
        if missing_keys:
            raise ValueError(f"Missing some input keys: {missing_keys}")

    def _validate_outputs(self, outputs: Dict[str, Any]) -> None:
        missing_keys = set(self.output_keys).difference(outputs)
        if missing_keys:
            raise ValueError(f"Missing some output keys: {missing_keys}")

    def prep_inputs(self, inputs: Union[Dict[str, Any], Any]) -> Dict[str, str]:
        """Validate and prep inputs."""
        if not isinstance(inputs, dict):
            _input_keys = set(self.input_keys)
            if self.memory is not None:
                # If there are multiple input keys, but some get set by memory so that
                # only one is not set, we can still figure out which key it is.
                _input_keys = _input_keys.difference(self.memory.memory_variables)
            if len(_input_keys) != 1:
                raise ValueError(
                    f"A single string input was passed in, but this chain expects "
                    f"multiple inputs ({_input_keys}). When a chain expects "
                    f"multiple inputs, please call it by passing in a dictionary, "
                    "eg `chain({'foo': 1, 'bar': 2})`"
                )
            inputs = {list(_input_keys)[0]: inputs}
        if self.memory is not None:
            external_context = self.memory.load_memory_variables(inputs)
            inputs = dict(inputs, **external_context)
        self._validate_inputs(inputs)
        return inputs

    def prep_outputs(self, inputs: Dict[str, str], outputs: Dict[str, str], return_only_outputs: bool = False) -> Dict[str, str]:
        """Validate and prep outputs."""
        self._validate_outputs(outputs)
        if self.memory is not None:
            self.memory.save_context(inputs, outputs)
        if return_only_outputs:
            return outputs
        else:
            return {**inputs, **outputs}

    @abc.abstractmethod
    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the chain."""

    def __call__(self, inputs: Dict[str, Any], return_only_outputs: bool = False) -> Dict[str, str]:
        """Execute the chain."""
        inputs = self.prep_inputs(inputs)
        try:
            outputs = self._call(inputs)
        except (KeyboardInterrupt, Exception) as e:
            raise e
        return self.prep_outputs(inputs, outputs, return_only_outputs)

    def run(self, *args: Any, **kwargs: Any) -> str:
        """Run the chain as text in, text out or multiple variables, text out."""
        if len(self.output_keys) != 1:
            raise ValueError(
                f"`run` not supported when there is not exactly "
                f"one output key. Got {self.output_keys}."
            )

        if args and not kwargs:
            if len(args) != 1:
                raise ValueError("`run` supports only one positional argument.")
            return self(args[0])[self.output_keys[0]]

        if kwargs and not args:
            return self(kwargs)[self.output_keys[0]]

        if not kwargs and not args:
            raise ValueError(
                "`run` supported with either positional arguments or keyword arguments,"
                " but none were provided."
            )

        raise ValueError(
            f"`run` supported with either positional arguments or keyword arguments"
            f" but not both. Got args: {args} and kwargs: {kwargs}."
        )