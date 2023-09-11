from dataclasses import dataclass

from uAgent.base import logger
from uAgent.agents.action import Action
from uAgent.chains.prompt import PromptTemplate
from uAgent.chains.output_parsers import CodeOutputParser

ROLE = """
You are a professional engineer; the main goal is to write PEP8 compliant, elegant, modular, easy to read and maintain Python 3.9 code (but you can also use other programming language)
ATTENTION: Use '##' to SPLIT SECTIONS, not '#'. Output format carefully referenced "Format example".

## Code: {filename} Write code with triple quoto, based on the following list and context.
1. Do your best to implement THIS ONLY ONE FILE. ONLY USE EXISTING API. IF NO API, IMPLEMENT IT.
2. Requirement: Based on the context, implement one following code file, note to return only in code form, your code will be part of the entire project, so please implement complete, reliable, reusable code snippets
3. Attention1: If there is any setting, ALWAYS SET A DEFAULT VALUE, ALWAYS USE STRONG TYPE AND EXPLICIT VARIABLE.
4. Attention2: YOU MUST FOLLOW "Data structures and interface definitions". DONT CHANGE ANY DESIGN.
5. Think before writing: What should be implemented and provided in this document?
6. CAREFULLY CHECK THAT YOU DONT MISS ANY NECESSARY CLASS/FUNCTION IN THIS FILE.
7. Do not use public member functions that do not exist in your design.
8. 代码中使用中文注释。
"""
PROMPT_TEMPLATE = """
-----
# Context
{context}
-----
"""

@dataclass
class WriteCode(Action):
    name: str = "WriteCode"
    role: str = ROLE
    lang: str = "python"

    def __post_init__(self):
        self.role = self.role.format(filename = self.filename)
        return super().__post_init__()

    def _is_invalid(self, filename):
        return any(i in filename for i in ["mp3", "wav"])

    def run(self, context):
        logger.info(f'Writing {self.filename}..')
        if self.filename is None:
            self.filename = input("Please input filename: ")
        self.role = self.role.format(filename = self.filename)
        self.llm.set_prompt(PromptTemplate(PROMPT_TEMPLATE))
        self.llm.set_output_parser(CodeOutputParser(lang=self.lang))
        self._ask(filename = self.filename, context = context)