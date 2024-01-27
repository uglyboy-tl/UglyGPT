#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from loguru import logger
import re

from uglychain import LLM, ReduceChain
from ..base import Action

ROLE = """
作为一个大型语言模型，你的任务是生成一个最终的摘要。
"""

PROMPT_TEMPLATE = """
我们已经提供了一个到某个点的现有摘要：
'''{history}'''
如果需要，我们有机会使用下面的更多上下文来改进现有的摘要。
'''{input}'''
根据新的上下文，优化原来的摘要。若原来的摘要不存在，则生成一个新的摘要。
如果这个上下文对你来说并不有用，那么就返回原来的摘要。
"""

@dataclass
class Summary(Action):
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE

    def __post_init__(self):
        self.llm = ReduceChain(self.prompt, self.model, self.role)
        return super().__post_init__()

    def run(self):
        data = self._load()
        parts = re.split('(?m)^(###(?!#))', data)
        parts = [parts[i-1] + parts[i] if i > 0 else parts[i] for i in range(0, len(parts), 2)]
        result = self.ask(input=parts)
        return result
        #logger.success(result)


