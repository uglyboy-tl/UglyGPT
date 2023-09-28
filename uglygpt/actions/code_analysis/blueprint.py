#!/usr/bin/env python3
# -*-coding:utf-8-*-
from dataclasses import dataclass
from pathlib import Path
import json

from loguru import logger

from uglygpt.actions.base import Action
from uglygpt.actions.utils import parse_json

IGNORE_EXTENSIONS = {'.bak'}

ROLE="""
你是一个程序架构分析师，正在分析一个源代码项目。
现在你已经看到了项目的目录结构，你需要：
- 根据目录结构来猜测每个目录可能的功能，并判断这个目录是否是重要目录，是否值得进一步分析。
    - 非根目录下的文件名只是帮助我们分析目录功能的，不用输出。
- 项目根目录下的文件往往是部署相关的文件或者是项目的入口文件(入口文件是重要文件)，也需要分析是否是重要文件，是否值得进一步分析。
    - 跟部署、版本控制、测试、临时文件等相关的文件/文件夹不是重要文件，我们只需要分析核心的源代码文件。
    - 资源文件(图片、视频、音频等)不是重要文件，我们只需要分析核心的源代码文件。

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
目录结构：
{tree}
请根据目录结构来猜测每个目录或根目录文件可能提供的功能，并判断这个目录/根目录文件是否重要，是否值得进一步分析。


"""

def get_directory_structure(path, depth=0, max_depth=3):
    base_dir = Path(path)
    dir_str = ""
    indent = '  ' * depth
    if base_dir.is_dir():
        for item in base_dir.iterdir():
            if item.name.startswith('.') or item.name == "__pycache__":
                continue
            if item.is_dir():
                dir_str += f"{indent}{item.name}/\n"
                if depth < max_depth:
                    dir_str += get_directory_structure(item, depth + 1, max_depth)
                else:
                    dir_str += f"{indent}  ...\n"
            else:
                if item.suffix in IGNORE_EXTENSIONS:
                    continue
                dir_str += f"{indent}{item.name}\n"
    return dir_str

@dataclass
class AnalysisBlueprint(Action):
    filename: str = "docs/examples/blueprint_analysis.json"
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE

    def run(self, path: str):
        tree = get_directory_structure(path)
        response = parse_json(self.llm(tree=tree))["result"]

        for item in response:
            if item["core"] == 1:
                logger.info(f"重要：{item['path']}，功能：{item['features']}")
            else:
                logger.info(f"不重要：{item['path']}，功能：{item['features']}")

        result = json.dumps(response, indent=4, ensure_ascii=False)
        self._save(result)
        return result


