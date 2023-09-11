from abc import abstractmethod
from typing import List

import re

from .base import BaseOutputParser


class ListOutputParser(BaseOutputParser):
    """Class to parse the output of an LLM call to a list."""

    @property
    def _type(self) -> str:
        return "list"

    @property
    def output_variables(self) -> List[str]:
        return ["list"]

    @abstractmethod
    def parse(self, text: str) -> List[str]:
        """Parse the output of an LLM call."""


class NumberedListOutputParser(ListOutputParser):
    """Parse out comma separated lists."""

    def get_format_instructions(self) -> str:
        return (
            "\nYour response should be a numbered list, "
            "eg: `1. First task\n2. Second task\n3. Third task`"
        )

    def parse(self, text: str) -> List[str]:
        """Parse the output of an LLM call."""
        result = re.split(r"\d+\.", text)
        return {"list": [r.strip() for r in result if r.strip()]}
