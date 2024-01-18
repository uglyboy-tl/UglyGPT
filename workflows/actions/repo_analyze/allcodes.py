#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Dict, List, Optional, Tuple

from loguru import logger

from uglygpt.base import File
from ..mapsqlite import MapSqlite
from uglygpt.chains import MapChain
from .utils import generate_dict, IMAGE_EXTENSIONS, MEDIA_EXTENSIONS, IGNORE_EXTENSIONS, EXTENSION_MAPPING

ROLE = """
作为一个熟练的软件工程师，你现在需要对一个特定的源代码项目进行深入研究，特别关注该项目试图解决的主要问题以及其解决方案。你需要对一个具体的项目文件进行详细分析，包括文件内容、文件名以及其他任何可用的信息。

你的任务是：
1. 概述文件的主要功能以及它是如何帮助解决项目的核心问题的。
2. 如果文件中包含业务逻辑，你需要识别并总结这些内容，这将有助于你更深入地理解项目的业务逻辑。
请注意，你的分析应更偏重于业务逻辑，而不是代码逻辑。例如，如果项目包含前端，你需要关注的是前端页面的功能（如登录、注册、购物车等）以及它与后端的交互或后端业务逻辑，而不是前端代码的具体实现。对于一个可以部署的项目，你需要关注的是项目解决特定问题的方法，而不是与部署相关的代码或项目的接口、架构。

对于那些对项目的重要性较低的文件，你只需要简要描述其基本功能。请确保你的回答简洁明了，只包含必要的信息，避免不必要的细节。
"""

PROMPT_TEMPLATE = """
{request}
-----
文件名：{file_name}
{additional}
文件内容:
{code}
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
                    code.append(f"```content```")
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
            request = OPTIONAL_REQUEST.format(message=message)
        directory_path = File.to_path(path)

        self.table = directory_path.name
        self._reset_cache()
        files, file_dict = self.filter_files(directory_path, filter)
        files, code, additional = self.fetch_files_data(files, file_dict)
        _data = self._load(files)
        new_files, code, additional = self.new_filter(files, code, additional, _data)

        assert len(files) > 0, "没有符合过滤器要求的文件"

        analysis_list = self.ask(file_name=new_files, code=code, additional=additional, request=request)
        analysis = {k:v for k,v in zip(files, analysis_list) if v != "Error"}
        _data.update(analysis)
        self._save(analysis)

        response = json.dumps(_data, indent=4, ensure_ascii=False)
        return response
