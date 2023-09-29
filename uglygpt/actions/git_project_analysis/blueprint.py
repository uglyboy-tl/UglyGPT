#!/usr/bin/env python3
# -*-coding:utf-8-*-
from dataclasses import dataclass
import json

from loguru import logger

from uglygpt.actions.base import Action
from uglygpt.actions.utils import parse_json
from .utils import get_directory_structure

ROLE = """
你是一个大型语言模型，专门训练用于分析和理解源代码项目的架构。你现在正在查看一个项目的目录结构。你的任务包括以下几个步骤：
1. 分析每个目录的可能功能。基于目录名和其下的文件名，尝试推测该目录的主要用途。例如，一个名为"controllers"的目录可能包含用于处理用户输入的代码。
2. 确定哪些目录是重要的，值得进一步分析。例如，如果一个目录包含大量核心功能的代码，那么它可能是重要的。
3. 分析项目根目录下的文件，判断它们是否是重要的。
重要的文件通常是与项目核心功能相关的源代码文件，如项目的入口文件。与部署、版本控制、测试、临时文件等相关的文件，以及资源文件（如图片、视频、音频等）不被视为重要文件。

你的输出应该是一个列表，其中包含你认为值得进一步分析的目录和文件。这个列表应该按照重要性排序，最重要的项目应该排在前面。

请按照以下示例格式直接返回 JSON 结果，其中 path 为文件或目录的路径，features 是对应文件（目录）为项目提供的功能，core 返回数字 0 或 1 分别表示对应文件（目录）不值得/值得进一步分析。请确保你返回的结果可以被 Python json.loads 解析。
格式示例：
{{"result":
    [
        {{"path": "{{目录路径或根目录下文件名}}", "features": "{{猜测该目录或文件可能的功能}}", "core": 1}},
        {{"path": "{{目录路径或根目录下文件名}}", "features": "{{猜测该目录或文件可能的功能}}", "core": 0}},
        ...
    ]
}}
"""

PROMPT_TEMPLATE = """
我将提供一个项目的目录结构，如下：
{tree}
我希望你能基于这个目录结构，对每个目录和根目录文件可能的功能进行推测。请针对每个目录或文件，描述你认为它可能的功能是什么，以及为什么你认为这个目录或文件是重要的，是否应该进行更深入的分析。你的分析应基于目录或文件的名称，位置，以及它们可能与其他目录或文件的关系。
"""


@dataclass
class AnalysisBlueprint(Action):
    filename: str = "docs/examples/analysis_blueprint.json"
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE

    def run(self, path: str):
        tree = get_directory_structure(path)
        response = parse_json(self.llm(tree=tree))["result"]
        result = json.dumps(response, indent=4, ensure_ascii=False)
        self._save(result)
        return result
