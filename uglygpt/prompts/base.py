import abc
import re
from typing import List, Optional
from .output_parsers.base import BaseOutputParser

class BasePromptTemplate(abc.ABC):
    input_variables: List[str]
    output_parser: Optional[BaseOutputParser] = None
    template: str

    def format_prompt(self, **kwargs):
        """Format the prompt with the given kwargs."""
        def replace(match):
            key = match.group(1)
            value = kwargs.get(key, match.group(0))
            if isinstance(value, list):
                return "".join(str(x) for x in value)
            else:
                return str(value)

        pattern = r"(?<!{){([^{}\n]+)}(?!})"
        result = re.sub(pattern, replace, self.template)
        return result
