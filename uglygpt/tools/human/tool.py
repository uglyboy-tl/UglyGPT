
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
from uglygpt.tools import BaseTool

def _print_func(text: str) -> None:
    print("\n")
    print(text)

@dataclass
class HumanInputRun(BaseTool):
    """Tool that adds the capability to ask user for input."""
    name: str = "Human"
    description: str = (
        "You can ask a human for guidance when you think you "
        "got stuck or you are not sure what to do next. "
        "The input should be a question for the human."
    )
    prompt_func: Callable[[str], None] = field(default_factory=lambda: _print_func)
    input_func: Callable = field(default_factory=lambda: input)

    def _run(
        self,
        query: str,
    ) -> str:
        """Use the Human input tool."""
        self.prompt_func(query)
        return self.input_func()