#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from loguru import logger

from uglygpt.chains import LLMChain
from uglygpt.actions.base import Action
from uglygpt.actions.utils import parse_markdown, parse_code


FORMAT = """- 请仔细参考 Format example 中的格式返回结果，尤其注意是使用'##'来分割章节，而不是'#'。
Format example：
## Reasoning
一步一步的解释你解决问题的思路，所有想说的都写在这里，不要写在代码的后面。
## Code
```python`
优化后的最终完整代码
```
"""

PROMPT_TEMPLATE = """
## Context
{context}
"""

@dataclass
class Developer(Action):
    prompt = PROMPT_TEMPLATE

    def __post_init__(self):
        if self.role:
            self.role = self.role.format(format=FORMAT)
        self.llm = LLMChain(llm_name="gpt4", prompt_template=self.prompt)
        return super().__post_init__()

    def _parse(self, text: str):
        response = parse_markdown(text)
        reasoning = response.get("Reasoning", "")
        code = response.get("Code", "")
        code = parse_code(code)
        return reasoning, code

    def run(self, *args, **kwargs):
        response = self.ask(*args, **kwargs)
        #logger.debug(response)
        reasoning, code = self._parse(response)
        logger.success(reasoning)
        self._save(code)
        return code