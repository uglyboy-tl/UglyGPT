import abc
import re
from typing import Any, List, Dict, Optional
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

    def _merge_partial_and_user_variables(self, **kwargs: Any) -> Dict[str, Any]:
        # Get partial params:
        partial_kwargs = {
            k: v if isinstance(v, str) else v()
            for k, v in self.partial_variables.items()
        }
        return {**partial_kwargs, **kwargs}

    @abc.abstractmethod
    def format(self, **kwargs: Any) -> str:
        """Format the prompt with the given kwargs."""
        pass