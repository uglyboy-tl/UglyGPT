# flake8: noqa
from __future__ import annotations
from typing import List, Dict, Any
from dataclasses import dataclass, field

from uglygpt.prompts import BasePromptTemplate, BaseOutputParser
from uglygpt.chains.novel.utils import get_content_between_a_b

_PROMPT_TEMPLATE = """
Now imagine you are a novelist writing a Chinese novel with the help of ChatGPT. You will be given a previously written paragraph (wrote by you), and a paragraph written by your ChatGPT assistant, a summary of the main storyline maintained by your ChatGPT assistant, and a plan of what to write next proposed by your ChatGPT assistant.
    I need you to write:
    1. Extended Paragraph: Extend the new paragraph written by the ChatGPT assistant to twice the length of the paragraph written by your ChatGPT assistant.
    2. Selected Plan: Copy the plan proposed by your ChatGPT assistant.
    3. Revised Plan: Revise the selected plan into an outline of the next paragraph.

    Previously written paragraph:
    {previous_paragraph}

    The summary of the main storyline maintained by your ChatGPT assistant:
    {memory}

    The new paragraph written by your ChatGPT assistant:
    {writer_new_paragraph}

    The plan of what to write next proposed by your ChatGPT assistant:
    {user_edited_plan}

    Now start writing, organize your output by strictly following the output format as below, 所有输出仍然保持是中文:

    Extended Paragraph:
    <string of output paragraph>, around 40-50 sentences.

    Selected Plan:
    <copy the plan here>

    Revised Plan:
    <string of revised plan>, keep it short, around 5-7 sentences.

    Very Important:
    Remember that you are writing a novel. Write like a novelist and do not move too fast when writing the plan for the next paragraph. Think about how the plan can be attractive for common readers when selecting and extending the plan. Remember to follow the length constraints! Remember that the chapter will contain over 10 paragraphs and the novel will contain over 100 chapters. And the next paragraph will be the second paragraph of the second chapter. You need to leave space for future stories.
"""

class _OutputParser(BaseOutputParser):
    @property
    def output_variables(self) -> List[str]:
        return [
            "output_paragraph",
            "output_instruction",
            # "memory"
        ]

    def parse(self, text: str) -> Dict[str]:
        try:
            if text.strip().splitlines()[0].startswith('Extended Paragraph'):
                new_paragraph = get_content_between_a_b(
                    'Extended Paragraph:', 'Selected Plan', text)
            else:
                new_paragraph = text.strip().splitlines()[0]

            lines = text.strip().splitlines()
            if lines[-1] != '\n' and lines[-1].startswith('Revised Plan:'):
                revised_plan = lines[-1][len("Revised Plan:"):]
            elif lines[-1] != '\n':
                revised_plan = lines[-1]

            output = {
                "output_paragraph": new_paragraph,
                # "selected_plan": selected_plan,
                "output_instruction": revised_plan,
                # "memory":self.input["output_memory"]
            }
            return output
        except:
            return None


@dataclass
class PreparePromptTemplate(BasePromptTemplate):
    input_variables: List[str] = field(default_factory=lambda: [
        "previous_paragraph",
        "memory",
        "writer_new_paragraph",
        "user_edited_plan"
    ])
    output_parser: BaseOutputParser = field(default_factory=_OutputParser)
    template: str = _PROMPT_TEMPLATE

    def format(self, **kwargs):
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        prompt = self.format_prompt(**kwargs)
        return prompt