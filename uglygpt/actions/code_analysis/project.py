#!/usr/bin/env python3
# -*-coding:utf-8-*-
from dataclasses import dataclass
from loguru import logger
from typing import List

from uglygpt.actions.base import Action
from uglygpt.chains import ReduceChain


ROLE = """
作为一个程序架构分析师，你现在需要继续阅读和分析另一批项目文件的报告。请根据这些新的信息，对你已经形成的分析报告进行修订和优化。这些新的分析结果可能包含一些细节信息，例如某个功能的具体实现，你需要筛选出有价值的信息。请记住，你的分析应以已有的报告为大纲进行，不要随意删除已有的内容。你的回答应当从全局的视角来看待整个项目，同时，你的回答应当简单明了，便于理解。
"""

PROMPT_TEMPLATE = """
现在，请你阅读并分析项目中的部分具体文件，这些文件的分析报告如下：
'''{analysis}'''

你已有的分析报告如下：
'''{history}'''

{request}
"""

DEFAULT_REQUEST = "请在分析后，总结并强调项目的核心内容，特别是项目想要解决的主要问题以及采取的主要解决方案。你应该对这些核心方法和业务逻辑进行详细的介绍。同时，如果遇到与核心功能或核心业务逻辑相关的文件，你应该适当地介绍其功能和作用。确保你的总结清晰、简洁，并能从全局角度理解整个项目。"

@dataclass
class AnalysisProject(Action):
    filename: str = "docs/examples/analysis_project.md"
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE

    def run(self, analysis: List[str], request: str = DEFAULT_REQUEST, history: str = ""):
        reduce = ReduceChain(chain=self.llm, reduce_keys=["analysis"])
        response = reduce(analysis=analysis, request=request, history=history)
        self._save(response)
        return response
