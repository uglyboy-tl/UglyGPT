#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from loguru import logger

from workflows.utils import parse_markdown, parse_code
from ..base import Action

FORMAT = """
请按照以下示例格式返回你的结果：
格式示例：

## Reasoning
在这部分，你需要用中文一步步地解释你的解决方案，包括你的思考过程和你为什么选择这种方案。所有需要解释的内容都应写在这里，而不是在代码后面。

## Code
```python
在这部分，你需要提供你的最终优化后的完整代码。
```
"""
PROMPT_TEMPLATE = """
## Context
{context}
"""

@dataclass
class Developer(Action):
    llm_name: str = "copilot-4"
    prompt: str = PROMPT_TEMPLATE
    name: str = ""

    def __post_init__(self):
        if self.role:
            self.role = self.role.format(format=FORMAT)
        return super().__post_init__()

    def _parse(self, text: str):
        response = parse_markdown(text)
        reasoning = response.get("Reasoning", "")
        code = response.get("Code", "")
        try:
            code = parse_code(code)
        except:
            logger.error(f"解析代码时出错，Reasoning: {reasoning}")
            raise
        return reasoning, code

    def run(self, *args, **kwargs):
        logger.info(f"正在执行 {self.name} 的任务...")
        response = self.ask(*args, **kwargs)
        reasoning, code = self._parse(response)
        logger.success(reasoning)
        self._save(code)
        return code