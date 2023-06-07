# flake8: noqa
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict

from uglygpt.prompts import BasePromptTemplate, BaseOutputParser
from uglygpt.chains.novel.utils import get_content_between_a_b

_PROMPT_TEMPLATE = """
Please write a {type} novel about {topic} with about 50 chapters. Follow the format below precisely:

    Begin with the name of the novel.
    Next, write an outline for the first chapter. The outline should describe the background and the beginning of the novel.
    Write the first three paragraphs with their indication of the novel based on your outline. Write in a novelistic style and take your time to set the scene.
    Write a summary that captures the key information of the three paragraphs.
    Finally, write three different instructions for what to write next, each containing around five sentences. Each instruction should present a possible, interesting continuation of the story.
"""

class _OutputParser(BaseOutputParser):
    @property
    def output_variables(self) -> List[str]:
        return [
            "name",
            "Outline",
            "Paragraph 1",
            "Paragraph 2",
            "Paragraph 3",
            "Summary",
            "Instruction 1",
            "Instruction 2",
            "Instruction 3"
        ]

    def parse(self, text: str) -> Dict[str]:
        paragraphs = {
            "name":"",
            "Outline":"",
            "Paragraph 1":"",
            "Paragraph 2":"",
            "Paragraph 3":"",
            "Summary": "",
            "Instruction 1":"",
            "Instruction 2":"",
            "Instruction 3":""
        }
        paragraphs['name'] = get_content_between_a_b('Name:','Outline',text)
        paragraphs['Paragraph 1'] = get_content_between_a_b('Paragraph 1:','Paragraph 2:',text)
        paragraphs['Paragraph 2'] = get_content_between_a_b('Paragraph 2:','Paragraph 3:',text)
        paragraphs['Paragraph 3'] = get_content_between_a_b('Paragraph 3:','Summary',text)
        paragraphs['Summary'] = get_content_between_a_b('Summary:','Instruction 1',text)
        paragraphs['Instruction 1'] = get_content_between_a_b('Instruction 1:','Instruction 2',text)
        paragraphs['Instruction 2'] = get_content_between_a_b('Instruction 2:','Instruction 3',text)
        lines = text.splitlines()
        # content of Instruction 3 may be in the same line with I3 or in the next line
        if lines[-1] != '\n' and lines[-1].startswith('Instruction 3'):
            paragraphs['Instruction 3'] = lines[-1][len("Instruction 3:"):]
        elif lines[-1] != '\n':
            paragraphs['Instruction 3'] = lines[-1]
        # Sometimes it gives Chapter outline, sometimes it doesn't
        for line in lines:
            if line.startswith('Chapter'):
                paragraphs['Outline'] = get_content_between_a_b('Outline:','Chapter',text)
                break
        if paragraphs['Outline'] == '':
            paragraphs['Outline'] = get_content_between_a_b('Outline:','Paragraph',text)

        return paragraphs

    def get_format_instructions(self) -> str:
        return """
    The output format should follow these guidelines:
    Name: <name of the novel>
    Outline: <outline for the first chapter>
    Paragraph 1: <content for paragraph 1>
    Paragraph 2: <content for paragraph 2>
    Paragraph 3: <content for paragraph 3>
    Summary: <content of summary>
    Instruction 1: <content for instruction 1>
    Instruction 2: <content for instruction 2>
    Instruction 3: <content for instruction 3>

    Make sure to be precise and follow the output format , 用中文输出.
"""

@dataclass
class InitPromptTemplate(BasePromptTemplate):
    output_parser: BaseOutputParser = field(default_factory=_OutputParser)
    template: str = _PROMPT_TEMPLATE

    @property
    def input_variables(self) -> List[str]:
        return ["type", "topic"]

    def format(self, **kwargs):
        kwargs = self._merge_partial_and_user_variables(**kwargs)
        prompt = self.format_prompt(**kwargs)
        prompt += self.output_parser.get_format_instructions()
        return prompt