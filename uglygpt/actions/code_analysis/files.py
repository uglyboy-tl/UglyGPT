#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Dict, List

from loguru import logger

from uglygpt.base import File
from uglygpt.actions.base import Action
from uglygpt.chains import MapChain

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif',
                    '.bmp', '.tiff', '.ico', '.jfif', '.webp'}
MEDIA_EXTENSIONS = {'.mp4', '.mp3', '.flv',
                    '.avi', '.mov', '.wmv', '.mkv', '.wav'}
IGNORE_EXTENSIONS = {'.bak'}

ROLE = """
你是一个程序架构分析师，正在分析一个源代码项目。
你分析项目的方式是先逐一分析每个文件，再进行汇总。分析结果需要注意：
- 分析本文件的功能是什么，最核心的模块有哪些，是如何发挥作用的；
- 留意文件之间的相互关系，便于后续整体分析时使用；
- 注意可以根据文件路径和文件名来辅助分析文件的可能功能；
- 你的回答必须简单明了，尽可能只保留必要的信息。
"""

PROMPT_TEMPLATE = """
{request}
下面是项目中具体文件的内容:
文件名：{file_name}
{additional}
文件内容:
```
{code}
```
"""

EXTENSION_MAPPING = {
    ".py": "python",
    ".md": "markdown",
    ".json": "json",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".js": "javascript",
    ".ts": "typescript",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".sh": "shell",
    ".bat": "bat",
    ".tsx": "tsx",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".swift": "swift",
    ".kt": "kotlin",
    ".rb": "ruby",
    ".pl": "perl",
    ".php": "php",
    ".lua": "lua",
    ".r": "r",
    ".scala": "scala",
    ".groovy": "groovy",
    ".ps1": "powershell",
    "txt": "text",
}

def generate_dict(file_list, file_dir_dict):
    # Convert relative paths in file_dir_dict to absolute paths
    absolute_file_dir_dict = {str(Path(key).resolve()): value for key, value in file_dir_dict.items()}

    parent_dict = {}
    new_dict = {}
    for file_path in file_list:
        path = Path(file_path)
        while path != Path('/'):
            path_str = str(path.resolve())
            if path_str in absolute_file_dir_dict:
                new_dict[file_path] = absolute_file_dir_dict[path_str]
                break
            elif path_str in parent_dict:
                new_dict[file_path] = absolute_file_dir_dict[parent_dict[path_str]]
                break
            else:
                parent = path.parent
                if str(parent.resolve()) in absolute_file_dir_dict:
                    parent_dict[path_str] = str(parent.resolve())
                path = parent
    return new_dict

@dataclass
class AnalysisEveryFile(Action):
    filename: str = "docs/examples/files_analysis.json"
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE

    def run(self, path: str, request: str = "请对项目文件做一个概述", filter: dict|None = None):
        chain = MapChain(self.llm, map_keys=["file_name", "code"])

        directory_path = Path(path)
        files = [
            path for path in directory_path.glob('**/*.*')
            if not any(part.startswith(".") or part == "__pycache__" for part in path.parts)
            and path.suffix not in IMAGE_EXTENSIONS
            and path.suffix not in MEDIA_EXTENSIONS
            and path.suffix not in IGNORE_EXTENSIONS
        ]

        file_dict = None
        if filter is not None:
            file_dict = generate_dict(files, filter)
            files = list(file_dict.keys())
        code = []
        invalid_files = []
        additional = []

        for file in files:
            try:
                content = file.read_text()
                if file.suffix in EXTENSION_MAPPING:
                    code.append(f"```{EXTENSION_MAPPING[file.suffix]}\n{content}\n```")
                else:
                    logger.warning(f"文件 {file} 类型未知，不进行额外处理")
                    code.append(content)
                additional.append(file_dict[file] if file_dict is not None else "")
            except Exception as e:
                logger.warning(f"文件 {file} 读取失败，错误信息：{e}")
                invalid_files.append(file)

        for file in invalid_files:
            files.remove(file)
        result = chain(file_name=files, code=code, additional = additional, request=request)
        code_analysis = json.loads(result)
        if len(code_analysis) != len(files):
            logger.error("处理结果的数量和文件数量不相等")

        analysis = dict()
        project_root = File.get_project_root(files[0])
        for i, file in enumerate(files):
            if code_analysis[i] == "Error":
                logger.warning(f"文件 {file} 分析失败")
                continue
            analysis[str(file.relative_to(project_root))] = code_analysis[i]

        response = json.dumps(analysis, indent=4, ensure_ascii=False)
        self._save(response)
        return response