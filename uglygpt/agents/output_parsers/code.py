import re
from dataclasses import dataclass
from typing import Dict, List, Any

from uAgent.base import logger
from uAgent.chains.output_parsers.base import BaseOutputParser

FORMAT_EXAMPLE = """
## Format example
-----
```{lang}
...
```
-----
"""


@dataclass
class CodeOutputParser(BaseOutputParser):
    lang: str = ""
    format_example: str = FORMAT_EXAMPLE

    @property
    def _type(self) -> str:
        return "code"

    @property
    def output_variables(self) -> List[str]:
        return ["code"]

    def get_format_instructions(self) -> str:
        return self.format_example.format(lang=self.lang)

    def parse(self, text: str, lang: str = None) -> Dict[str, Any]:
        if lang is None:
            lang = self.lang
        pattern = rf'```{lang}.*?\s+(.*?)```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            logger.error(f"{pattern} not match following text:")
            logger.error(text)
            raise Exception
        return {"code": code}
