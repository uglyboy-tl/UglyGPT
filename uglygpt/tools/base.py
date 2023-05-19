import abc
from dataclasses import dataclass
from inspect import signature, Parameter
from typing import Any, Dict, Tuple, Optional, Union, Callable


@dataclass
class BaseTool(abc.ABC):
    name: str
    description: str
    return_direct: bool = False

    @property
    def args(self) -> dict:
        params = {}
        sig = signature(self._run)
        for name, param in sig.parameters.items():
            if param.default == Parameter.empty:
                params[name] = None
            else:
                params[name] = param.default
        return params

    def _parse_input(
        self,
        tool_input: Union[str, Dict],
    ) -> Union[str, Dict[str, Any]]:
        """Convert tool input to pydantic model."""
        input_args = self.args
        if isinstance(tool_input, str):
            if input_args is not None:
                key_ = next(iter(input_args.keys()))
            return tool_input
        else:
            if input_args is not None:
                return {k: v for k, v in tool_input if k in input_args.keys()}
        return tool_input

    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        # For backwards compatibility, if run_input is a string,
        # pass as a positional argument.
        if isinstance(tool_input, str):
            return (tool_input,), {}
        else:
            return (), tool_input

    @abc.abstractmethod
    def _run(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        # For backwards compatibility, if run_input is a string,
        # pass as a positional argument.
        if isinstance(tool_input, str):
            return (tool_input,), {}
        else:
            return (), tool_input

    def run(self, tool_input: Union[str, Dict], **kwargs: Any) -> Any:
        parsed_input = self._parse_input(tool_input)
        try:
            tool_args, tool_kwargs = self._to_args_and_kwargs(parsed_input)
            observation = self._run(*tool_args, **tool_kwargs)
        except (Exception, KeyboardInterrupt) as e:
            raise e
        return observation

@dataclass
class Tool(BaseTool):
    """Tool that takes in function or coroutine directly."""
    description: str = ""
    func: Callable[..., str] = None
    """The function to run when the tool is called."""

    @property
    def args(self) -> dict:
        """The tool's input arguments."""
        return {"tool_input": {"type": "string"}}

    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        """Convert tool input to pydantic model."""
        args, kwargs = super()._to_args_and_kwargs(tool_input)
        # For backwards compatibility. The tool must be run with a single input
        all_args = list(args) + list(kwargs.values())
        if len(all_args) != 1:
            raise ValueError(
                f"Too many arguments to single-input tool {self.name}."
                f" Args: {all_args}"
            )
        return tuple(all_args), {}

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Use the tool."""
        return self.func(*args, **kwargs)

    # TODO: this is for backwards compatibility, remove in future
    def __init__(
        self, name: str, func: Callable, description: str, **kwargs: Any
    ) -> None:
        """Initialize tool."""
        super(Tool, self).__init__(
            name=name, func=func, description=description, **kwargs
        )

    @classmethod
    def from_function(
        cls,
        func: Callable,
        name: str,  # We keep these required to support backwards compatibility
        description: str,
        return_direct: bool = False,
        **kwargs: Any,
    ):
        """Initialize tool from a function."""
        return cls(
            name=name,
            func=func,
            description=description,
            return_direct=return_direct,
            **kwargs,
        )


class StructuredTool(BaseTool):
    """Tool that can operate on any number of inputs."""

    description: str = ""
    """The input arguments' schema."""
    func: Callable[..., Any]
    """The function to run when the tool is called."""

    def _run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Use the tool."""
        return self.func(*args, **kwargs)

    @classmethod
    def from_function(
        cls,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        return_direct: bool = False,
        **kwargs: Any,
    ):
        name = name or func.__name__
        description = description or func.__doc__
        assert (
            description is not None
        ), "Function must have a docstring if description not provided."

        # Description example:
        # search_api(query: str) - Searches the API for the query.
        description = f"{name}{signature(func)} - {description.strip()}"

        return cls(
            name=name,
            func=func,
            description=description,
            return_direct=return_direct,
            **kwargs,
        )
