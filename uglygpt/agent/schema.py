from __future__ import annotations
from abc import abstractmethod
from typing import NamedTuple, Union

from uglygpt.prompts import BaseOutputParser

class AgentAction(NamedTuple):
    """Agent's action to take."""

    tool: str
    tool_input: Union[str, dict]
    log: str


class AgentFinish(NamedTuple):
    """Agent's return value."""

    return_values: dict
    log: str

class AgentOutputParser(BaseOutputParser):
    @abstractmethod
    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        """Parse text into agent action/finish."""