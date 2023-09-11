from dataclasses import dataclass

from uAgent.base import logger, WORKSPACE_ROOT
from uAgent.agents.action import Action
from uAgent.chains.prompt import PromptTemplate
from uAgent.chains.output_parsers import CodeOutputParser

ROLE = """
你是一名专业的工程师，主要目标是将目标代码改写成符合PEP8标准，设计优雅、模块化、易于阅读和维护的Python 3.9代码（但你也可以使用其他编程语言）。
注意：使用'##'来分割章节，而不是'#'。输出格式请参考"Format example"。

## 代码改写：根据下文 Context 中的要求和下列要求，对 Code 中的代码进行改写，尽你所能优化这个文件，并写出修改建议（最多5条）。
```
1. 使用中文注释，注释内容应该清晰明确，不要使用拼音；
2. 不要修改原 Code 中的数据结构和接口定义，除非在 Context 中有明确要求；
```
"""

PROMPT_TEMPLATE = """

## Rewrite Code: {filename} Base on "Context" and the source code, rewrite code with triple quotes. Do your utmost to optimize THIS SINGLE FILE.
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
class ChangeCode(Action):
    name: str = "ChangeCode"
    role: str = ROLE
    lang: str = "python"

    def run(self, context):
        filename = self.filename
        logger.info(f'Code changing {filename}..')
        code = self._load()
        self.filename = self.filename + ".new"
        self.llm.set_prompt(PromptTemplate(PROMPT_TEMPLATE))
        self.llm.set_output_parser(CodeOutputParser(lang=self.lang, format_example=FORMAT_EXAMPLE.format(filename=filename, lang=self.lang)))
        self._ask(context=context, code=code, filename=filename)