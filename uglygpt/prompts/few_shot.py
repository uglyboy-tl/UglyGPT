"""Prompt template that contains few shot examples."""
from typing import Any, Dict, List, Optional

from uglygpt.prompts.base import BasePromptTemplate
from uglygpt.prompts.example_selector.base import BaseExampleSelector


class FewShotPromptTemplate(BasePromptTemplate):
    """Prompt template that contains few shot examples."""
    def __init__(
            self,
            input_variables: List[str],
            example_prompt: BasePromptTemplate,
            suffix: str,
            examples: Optional[List[dict]] = None,
            example_selector: Optional[BaseExampleSelector] = None,
            prefix: str = "",
            example_separator: str = "\n\n",
            template_format: str = "f-string",
            validate_template: bool = True,
            ) -> None:
        """Initialize the prompt template.

        Args:
            input_variables: A list of the names of the variables the prompt template expects.
            example_prompt: PromptTemplate used to format an individual example.
            suffix: A prompt template string to put after the examples.
            examples: Examples to format into the prompt. Either this or example_selector should be provided.
            example_selector: ExampleSelector to choose the examples to format into the prompt. Either this or examples should be provided.
            prefix: A prompt template string to put before the examples.
            example_separator: String separator used to join the prefix, the examples, and suffix.
            template_format: The format of the prompt template. Options are: 'f-string', 'jinja2'.
            validate_template: Whether or not to try validating the template.
        """
        self.input_variables = input_variables
        self.example_prompt = example_prompt
        self.suffix = suffix
        self.examples = examples
        self.example_selector = example_selector
        self.prefix = prefix
        self.example_separator = example_separator
        self.template_format = template_format
        self.validate_template = validate_template


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