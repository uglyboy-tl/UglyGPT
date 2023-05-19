"""Prompt template that contains few shot examples."""
from dataclasses import dataclass,field
from typing import Any, Dict, List, Optional

from uglygpt.prompts import PromptTemplate, BasePromptTemplate
from uglygpt.prompts.example_selector.base import BaseExampleSelector

@dataclass
class FewShotPromptTemplate(BasePromptTemplate):
    """Prompt template that contains few shot examples."""
    input_variables: List[str] = field(default_factory=list)
    example_prompt: BasePromptTemplate = field(default_factory=PromptTemplate)
    suffix: str = ""
    examples: Optional[List[dict]] = None
    example_selector: Optional[BaseExampleSelector] = None
    prefix: str = ""
    example_separator: str = "\n\n"

    def _get_examples(self, **kwargs: Any) -> List[dict]:
        if self.examples is not None:
            return self.examples
        elif self.example_selector is not None:
            return self.example_selector.select_examples(kwargs)
        else:
            raise ValueError

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
        # Get the examples to use.
        examples = self._get_examples(**kwargs)
        examples = [
            {k: e[k] for k in self.example_prompt.input_variables} for e in examples
        ]
        # Format the examples.
        example_strings = [
            self.example_prompt.format(**example) for example in examples
        ]
        # Create the overall template.
        pieces = [self.prefix, *example_strings, self.suffix]
        self.template = self.example_separator.join([piece for piece in pieces if piece])

        # Format the template with the input variables.
        prompt = self.format_prompt(**kwargs)
        return prompt

    @property
    def _prompt_type(self) -> str:
        """Return the prompt type key."""
        return "few_shot"

    def dict(self, **kwargs: Any) -> Dict:
        """Return a dictionary of the prompt."""
        if self.example_selector:
            raise ValueError("Saving an example selector is not currently supported")
        return super().dict(**kwargs)