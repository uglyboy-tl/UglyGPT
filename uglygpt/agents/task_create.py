#!/usr/bin/env python3
#-*-coding:utf-8-*-

from dataclasses import dataclass

from .action import Action
from .utils import file_list_parse
from uglygpt.base import logger
from uglygpt.chains.prompt import Prompt

ROLE = """
你是一名任务创建工程师，你需要根据你的目标任务：`{objective}`，来创建一个任务列表。
1. 任务列表是一个列表，列表中的每一项都是一个任务，这些任务都可以通过脚本完成（会有专门的脚本工程师来编写脚本）。
2. 任务是一个字符串，描述了任务的内容，型如：`"具体的任务描述..."`。
3. 任务列表中的任务是有顺序的，你需要按照你的目标任务的顺序来创建任务列表。
4. 任务列表尽可能精简，不要包含无关的任务。一些不确定的任务后续有专门的任务创建工程师来创建。
5. 去掉已经完成的任务。
6. 如果目标任务已经完成，你可以不用创建任务列表。
"""
CONTENT_TEMPLATE = """
-----
## Context
{context}
"""
PROMPT_TEMPLATE = """
## 原有任务列表
{tasks}
## 刚刚完成的任务
{task}
## 任务执行结果
{result}
"""
format_example = """
-----
## Format example
---
## 解决思路
解决目标问题的思路。
## 任务列表
```python
[
    "task1",
]
```
---
"""

@dataclass
class TaskCreation(Action):
    role: str = ROLE
    objective: str = ""

    def __post_init__(self):
        self.role = self.role.format(objective = self.objective)
        logger.debug(f'Role: {self.role}')
        return super().__post_init__()

    def run(self, context = "", tasks = None, task = None, result="") -> str:
        logger.info(f'Task Creating ..')
        if task is not None:
            self.llm.set_prompt(Prompt(CONTENT_TEMPLATE + PROMPT_TEMPLATE + format_example))
            rp = self._ask(tasks = tasks, task = task, result = result, context = context)
        else:
            self.llm.set_prompt(Prompt(CONTENT_TEMPLATE + format_example))
            rp = self._ask(context = context)
        return rp

    def _parse(self, text: str):
        return file_list_parse(text)