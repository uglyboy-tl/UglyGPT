from dataclasses import dataclass

from uAgent.base import logger, WORKSPACE_ROOT
from uAgent.agents.action import Action
from uAgent.chains.prompt import PromptTemplate
from uAgent.chains.output_parsers import CodeOutputParser

ROLE = """
You are a professional software engineer, and your main task is to review the code. You need to ensure that the code conforms to the PEP8 standards, is elegantly designed and modularized, easy to read and maintain, and is written in Python 3.9 (or in another programming language).
ATTENTION: Use '##' to SPLIT SECTIONS, not '#'. Output format carefully referenced "Format example".

## Code Review: Based on the following context and code, and following the check list, Provide key, clear, concise, and specific code modification suggestions, up to 5.
```
1. Check 0: Is the code implemented as per the requirements?
2. Check 1: Are there any issues with the code logic?
3. Check 2: Does the existing code follow the "Data structures and interface definitions"?
4. Check 3: Is there a function in the code that is omitted or not fully implemented that needs to be implemented?
5. Check 4: Does the code have unnecessary or lack dependencies?
```
"""

PROMPT_TEMPLATE = """

## Rewrite Code: {filename} Base on "Code Review" and the source code, rewrite code with triple quotes. Do your utmost to optimize THIS SINGLE FILE.
-----
# Context
{context}

## Code: {filename}
```
{code}
```
-----
"""

FORMAT_EXAMPLE = """

## Code Review
1. The code ...
2. ...
3. ...
4. ...
5. ...

## Rewrite Code: {filename}
```{lang}
## {filename}
...
```
"""

@dataclass
class WriteCodeReview(Action):
    name: str = "WriteCodeReview"
    role: str = ROLE
    lang: str = "python"

    def _save(self, filename, code):
        code_path = WORKSPACE_ROOT / filename
        code_path.parent.mkdir(parents=True, exist_ok=True)
        code_path.write_text(code)
        logger.info(f"Saving Code to {code_path}")

    def run(self, context, filename):
        logger.info(f'Code review {filename}..')
        self.filename = filename
        code = self._load()
        self.llm.set_prompt(PromptTemplate(PROMPT_TEMPLATE))
        self.llm.set_output_parser(CodeOutputParser(lang=self.lang, format_example=FORMAT_EXAMPLE.format(filename=filename, lang=self.lang)))
        self._ask(context=context, code=code, filename=filename)