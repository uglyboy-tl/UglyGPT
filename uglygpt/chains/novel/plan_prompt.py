# flake8: noqa
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict

from uglygpt.prompts import BasePromptTemplate, BaseOutputParser
from uglygpt.chains.novel.utils import get_content_between_a_b

_PROMPT_TEMPLATE = """
Now imagine you are a helpful assistant that help a novelist with decision making. You will be given a previously written paragraph and a paragraph written by a ChatGPT writing assistant, a summary of the main storyline maintained by the ChatGPT assistant, and 3 different possible plans of what to write next.
    I need you to:
    Select the most interesting and suitable plan proposed by the ChatGPT assistant.

    Previously written paragraph:
    {previous_paragraph}

    The summary of the main storyline maintained by your ChatGPT assistant:
    {memory}

    The new paragraph written by your ChatGPT assistant:
    {writer_new_paragraph}

    Three plans of what to write next proposed by your ChatGPT assistant:
    {previous_plans}

"""

class _OutputParser(BaseOutputParser):
    @property
    def output_variables(self) -> List[str]:
        return [
            "Selected Plan",
            "Reason"
        ]

    def parse(self, text: str) -> Dict[str]:
        plan = get_content_between_a_b('Selected Plan:','Reason',text)
        lines = text.strip().splitlines()
        if lines[-1] != '\n' and lines[-1].startswith('Reason:'):
            reason = lines[-1][len("Reason:"):]
        elif lines[-1] != '\n':
            reason = lines[-1]
        return {"Selected Plan": plan, "Reason": reason}

    def get_format_instructions(self) -> str:
        return """
    Now start choosing, organize your output by strictly following the output format as below, 用中文输出:

    Selected Plan:
    <copy the selected plan here>

    Reason:
    <Explain why you choose the plan>
"""

@dataclass
class PlanPromptTemplate(BasePromptTemplate):
    input_variables: List[str] = field(default_factory=lambda: [
        "previous_paragraph",
        "memory",
        "writer_new_paragraph",
        "previous_plans"
    ])
    output_parser: BaseOutputParser = field(default_factory=_OutputParser)
    template: str = _PROMPT_TEMPLATE

    def format(self, **kwargs):
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        prompt = self.format_prompt(**kwargs)
        prompt += self.output_parser.get_format_instructions()
        return prompt