from uglygpt.prompts.base import BasePromptTemplate
from typing import Any, List

class PromptTemplate(BasePromptTemplate):
    """Schema to represent a prompt for an LLM.

    Example:
        .. code-block:: python

            from langchain import PromptTemplate
            prompt = PromptTemplate(input_variables=["foo"], template="Say {foo}")
    """
    def __init__(self, input_variables:List[str], template: str) -> None:
        """A list of the names of the variables the prompt template expects."""
        self.input_variables = input_variables
        """The prompt template."""
        self.template = template

    @property
    def _prompt_type(self) -> str:
        """Return the prompt type key."""
        return "prompt"

    def format(self, **kwargs: Any) -> str:
        """Format the prompt with the inputs.

        Args:
            kwargs: Any arguments to be passed to the prompt template.

        Returns:
            A formatted string.

        Example:

        .. code-block:: python

            prompt.format(variable1="foo")
        """
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        return self.format_prompt(**kwargs)