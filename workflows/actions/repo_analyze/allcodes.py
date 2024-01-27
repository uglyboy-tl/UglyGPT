#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Dict, List, Optional, Tuple

from loguru import logger

from workflows.utils import File
from ..mapsqlite import MapSqlite
from .utils import generate_dict, IMAGE_EXTENSIONS, MEDIA_EXTENSIONS, IGNORE_EXTENSIONS, EXTENSION_MAPPING

ROLE = """
你是一位资深的程序员，正在帮一位新手程序员阅读某个开源项目，我会把每个文件的内容告诉你，你需要做一个新手程序员阅读的，简单明了的总结。用MarkDown格式返回（必要的话可以用emoji表情增加趣味性）
"""

PROMPT_TEMPLATE = """
源文件路径：{file_name}，源代码：\n{code}
"""

DEFAULT_REQUEST = "请对以下项目文件进行分析"
OPTIONAL_REQUEST = "这是关于项目的一些信息{message},请结合相关内容对以下项目文件进行分析"

@dataclass
class AllCodes(MapSqlite):
    filename: str = "resource/analysis_allcodes.db"
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE
    map_keys: List[str] = field(default_factory=lambda: ["file_name", "code"])


    def filter_files(self, directory_path: Path, filter: Optional[Dict[str, str] | Dict[Path, str]] = None) -> Tuple[List[Path], Optional[Dict[Path, str]]]:
        image_extensions = set(IMAGE_EXTENSIONS)
        media_extensions = set(MEDIA_EXTENSIONS)
        ignore_extensions = set(IGNORE_EXTENSIONS)

        files = [
            path for path in directory_path.glob('**/*.*')
            if not any(part.startswith(".") or part == "__pycache__" for part in path.parts)
            and path.suffix not in image_extensions
            and path.suffix not in media_extensions
            and path.suffix not in ignore_extensions
        ]

        if filter is not None:
            file_dict = generate_dict(files, filter)
            files = list(file_dict.keys())
        else:
            file_dict = None

        return files, file_dict

    def fetch_files_data(self, files: List[Path], file_dict: Optional[Dict]) -> Tuple[List[str], List[str], List[str]]:
        code = []
        invalid_files = []
        additional = []

        for file in files:
            try:
                content = file.read_text()
                if file.suffix.lower() in EXTENSION_MAPPING:
                    code.append(
                        f"```{EXTENSION_MAPPING[file.suffix.lower()]}\n{content}\n```")
                else:
                    logger.warning(f"文件 {file} 类型未知，不进行额外处理")
                    code.append("```content```")
                additional.append(
                    file_dict[file] if file_dict is not None else "")
            except Exception as e:
                logger.error(f"文件 {file} 读取失败，错误信息：{e}")
                invalid_files.append(file)

        for file in invalid_files:
            files.remove(file)

        project_root = File.get_project_root(files[0])
        short_name_files = [str(file.relative_to(project_root)) for file in files]
        return short_name_files, code, additional

    def new_filter(self, files: List[str], code: List[str], additional: List[str], data: Dict[str, str]):
        new_files = [i for i in files]
        new_code = [i for i in code]
        new_additional = [i for i in additional]
        for i in range(len(files)):
            if files[i] in data.keys():
                new_files.pop(i)
                new_code.pop(i)
                new_additional.pop(i)
        return new_files, new_code, new_additional


    def run(self, path: str, request: str = DEFAULT_REQUEST, filter: Optional[Dict[str, str] | Dict[Path, str]] = None, message: Optional[str] = None) -> str:
        if message is not None:
            request = OPTIONAL_REQUEST.format(message=message)  # noqa: F841
        directory_path = File.to_path(path)

        self.table = directory_path.name
        self._reset_cache()
        files, file_dict = self.filter_files(directory_path, filter)
        files, code, additional = self.fetch_files_data(files, file_dict)
        _data = self._load(files)
        new_files, code, additional = self.new_filter(files, code, additional, _data)

        assert len(files) > 0, "没有符合过滤器要求的文件"

        analysis_list = self.ask(file_name=new_files, code=code)
        analysis = {k:v for k,v in zip(files, analysis_list) if v != "Error"}
        _data.update(analysis)
        self._save(analysis)

        response = json.dumps(_data, indent=4, ensure_ascii=False)
        return response
