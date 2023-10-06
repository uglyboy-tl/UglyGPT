#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from loguru import logger
from typing import List

from uglygpt.actions.base import Action
from uglygpt.chains import ReduceChain


ROLE = """
作为一个程序架构分析师，你现在需要继续阅读和分析另一批项目文件的报告。请根据这些新的信息，对你已经形成的分析报告进行修订和优化。这些新的分析结果可能包含一些细节信息，例如某个功能的具体实现，你需要筛选出有价值的信息。请记住，你的分析应以已有的报告为大纲进行，不要随意删除已有的内容。你的回答应当从全局的视角来看待整个项目，同时，你的回答应当简单明了，便于理解。你的回答请直接返回新的分析报告。
"""

PROMPT_TEMPLATE = """
我们已经提供了一个到某个点的分析报告：
'''{history}'''
如果需要，我们有机会使用下面的更多上下文来改进现有的分析报告。
'''{analysis}'''
根据新的上下文，优化原来的分析报告。
如果这个上下文对你来说并不有用，那么就返回原来的分析报告。

分析报告的格式要求：
{format}
"""

DEFAULT_FORMAT = """
# <项目名称>
## 项目背景
<介绍项目要解决的问题，和使用的核心解决手段，以及其他一些重要的跟项目相关的信息>
## 项目状况
<介绍项目的当前状况，包括项目网址、项目使用的编程语言、标签、最近更新时间，最近更新次数，项目的 Star 数、Fork 数、讨论数等等各种信息，我们掌握的跟项目整体状况有关的信息都可以在这里列出来>
## 项目结构
<介绍项目的整体结构，包括项目主要的文件、主要的函数、主要的类等等，这部分可以用 markdown 表格的形式来展现>
"""

@dataclass
class Conclusion(Action):
    filename: str = "docs/examples/analysis_conclusion.md"
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE

    def run(self, analysis: List[str], format: str = DEFAULT_FORMAT, history: str = ""):
        reduce = ReduceChain(chain=self.llm, reduce_keys=["analysis"])
        response = reduce(analysis=analysis, format=format, history=history)
        self._save(response)
        return response
