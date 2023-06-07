# flake8: noqa
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict

from uglygpt.prompts import BasePromptTemplate, BaseOutputParser
from uglygpt.chains.novel.utils import get_content_between_a_b

_PROMPT_TEMPLATE = """I need you to help me write a novel. Now I give you a memory (a brief summary) of 400 words, you should use it to store the key content of what has been written so that you can keep track of very long context. For each time, I will give you your current memory (a brief summary of previous stories. You should use it to store the key content of what has been written so that you can keep track of very long context), the previously written paragraph, and instructions on what to write in the next paragraph. 
I need you to write:
1. Output Paragraph: the next paragraph of the novel. The output paragraph should contain around 20 sentences and should follow the input instructions.
2. Output Memory: The updated memory. You should first explain which sentences in the input memory are no longer necessary and why, and then explain what needs to be added into the memory and why. After that you should write the updated memory. The updated memory should be similar to the input memory except the parts you previously thought that should be deleted or added. The updated memory should only store key information. The updated memory should never exceed 20 sentences!
3. Output Instruction:  instructions of what to write next (after what you have written). You should output 3 different instructions, each is a possible interesting continuation of the story. Each output instruction should contain around 5 sentences
Here are the inputs:

Input Memory:
{short_memory}

Input Paragraph:
{input_paragraph}

Input Instruction:
{input_instruction}

Input Related Paragraphs:
{input_long_term_memory}

Now start writing, organize your output by strictly following the output format as below:
Output Paragraph:
<string of output paragraph>, around 20 sentences.

Output Memory:
Rational: <string that explain how to update the memory>;
Updated Memory: <string of updated memory>, around 10 to 20 sentences

Output Instruction:
Instruction 1: <content for instruction 1>, around 5 sentences
Instruction 2: <content for instruction 2>, around 5 sentences
Instruction 3: <content for instruction 3>, around 5 sentences

Very important!! The updated memory should only store key information. The updated memory should never contain over 500 words!
Finally, remember that you are writing a novel. Write like a novelist and do not move too fast when writing the output instructions for the next paragraph. Remember that the chapter will contain over 10 paragraphs and the novel will contain over 100 chapters. And this is just the beginning. Just write some interesting staffs that will happen next. Also, think about what plot can be attractive for common readers when writing output instructions.

Very Important:
You should first explain which sentences in the input memory are no longer necessary and why, and then explain what needs to be added into the memory and why. After that, you start rewrite the input memory to get the updated memory.
{new_character_prompt}
"""

class _OutputParser(BaseOutputParser):
    @property
    def output_variables(self) -> List[str]:
        return [
            "output_memory",
            "output_paragraph",
            "output_instruction",
        ]

    def parse(self, text: str) -> Dict[str]:
        try:
            output_paragraph = get_content_between_a_b(
                'Output Paragraph:', 'Output Memory', text)
            output_memory_updated = get_content_between_a_b(
                'Updated Memory:', 'Output Instruction:', text)
            self.short_memory = output_memory_updated
            ins_1 = get_content_between_a_b(
                'Instruction 1:', 'Instruction 2', text)
            ins_2 = get_content_between_a_b(
                'Instruction 2:', 'Instruction 3', text)
            lines = text.splitlines()
            # content of Instruction 3 may be in the same line with I3 or in the next line
            if lines[-1] != '\n' and lines[-1].startswith('Instruction 3'):
                ins_3 = lines[-1][len("Instruction 3:"):]
            elif lines[-1] != '\n':
                ins_3 = lines[-1]

            output_instructions = [ins_1, ins_2, ins_3]
            assert len(output_instructions) == 3

            text = {
                "output_memory": output_memory_updated,  # feed to human
                "output_paragraph": output_paragraph,
                "output_instruction": [instruction.strip() for instruction in output_instructions]
            }

            return text
        except:
            return None


@dataclass
class NovelPromptTemplate(BasePromptTemplate):
    output_parser: BaseOutputParser = field(default_factory=_OutputParser)
    template: str = _PROMPT_TEMPLATE

    @property
    def input_variables(self) -> List[str]:
        return [
            "short_memory",
            "input_paragraph",
            "input_instruction",
            "input_long_term_memory",
        ]

    def format(self, **kwargs):
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        prompt = self.format_prompt(**kwargs)
        return prompt