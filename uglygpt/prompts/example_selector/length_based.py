"""Select examples based on length."""
import re
from typing import Callable, Dict, List

from uglygpt.prompts.example_selector.base import BaseExampleSelector
from uglygpt.prompts.base import BasePromptTemplate


def _get_length_based(text: str) -> int:
    return len(re.split("\n| ", text))


class LengthBasedExampleSelector(BaseExampleSelector):
    """Select examples based on length."""

    examples: List[dict]
    """A list of the examples that the prompt template expects."""

    example_prompt: BasePromptTemplate
    """Prompt template used to format the examples."""

    get_text_length: Callable[[str], int] = _get_length_based
    """Function to measure prompt length. Defaults to word count."""

    max_length: int = 2048
    """Max length for the prompt, beyond which examples are cut."""

    example_text_lengths: List[int] = []  #: :meta private:

    def add_example(self, example: Dict[str, str]) -> None:
        """Add new example to list."""
        self.examples.append(example)
        string_example = self.example_prompt.format(**example)
        self.example_text_lengths.append(self.get_text_length(string_example))

    def select_examples(self, input_variables: Dict[str, str]) -> List[dict]:
        """Select which examples to use based on the input lengths."""
        inputs = " ".join(input_variables.values())
        remaining_length = self.max_length - self.get_text_length(inputs)
        i = 0
        examples = []
        while remaining_length > 0 and i < len(self.examples):
            new_length = remaining_length - self.example_text_lengths[i]
            if new_length < 0:
                break
            else:
                examples.append(self.examples[i])
                remaining_length = new_length
            i += 1
        return examples