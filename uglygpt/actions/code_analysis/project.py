#!/usr/bin/env python3
# -*-coding:utf-8-*-
from dataclasses import dataclass
from loguru import logger
from typing import List

from uglygpt.actions.base import Action
from uglygpt.chains import ReduceChain


ROLE="""
你是一个程序架构分析师，正在分析一个源代码项目。
你已经阅读了一些文件的分析报告，现在要继续阅读另一批文件的分析报告，并进行更加综合的分析：
- 根据已有的分析结果，进行更加综合的分析，尽量将已有的分析结果进行整合，获得更加全面的分析结果；
- 请留意文件之间的相互关系，可以参考已知的文件的分析来增强对新文件的分析，也可以根据新文件的分析来更新已有文件的分析；
- 可以根据新内容来更新已有的分析结果，但是不要删除已有的分析结果；
- 你的回答必须简单明了，尽可能只保留必要的信息。
"""
PROMPT_TEMPLATE = """
通过过去的分析，你已经通过一些文件的分析报告了解了一些情况，如下:
{history}
请继续分析其他文件的分析报告，从而更全面地理解整个项目。报告如下：
{analysis}
-----
{request}
"""

@dataclass
class AnalysisProject(Action):
    filename: str = "docs/examples/project_analysis.md"
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE

    def run(self, analysis: List[str], request: str = "用一张Markdown表格输出你的分析结果，列出每个文件实现功能的解读。"):
        reduce = ReduceChain(chain=self.llm, reduce_keys=["analysis"])
        response = reduce(analysis=analysis, request=request)
        self._save(response)
        return response
