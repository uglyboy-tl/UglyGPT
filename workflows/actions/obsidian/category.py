#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum, unique

from loguru import logger
from pydantic import BaseModel, Field

from ..mapsqlite import MapSqlite

ROLE = """我将提供一些项目的描述信息。请根据这些信息，将每个项目分类到以下类别中的一个：
- `AI`: 关于机器学习或人工智能的项目；
- `前端`: 前端相关的技术，例如 Vue、React等等生态下的种种技术，也包括移动客户端、小程序的技术，图标、字体等也属于这里；
- `后端`: 这里主要指可以 selfhost 的后端服务类项目，而不是技术框架。例如，一个可以自己搭建的博客系统，或者一个可以自己搭建的 RSS 服务等等；如果是某个 Go 的 Web 框架，或者某个 Java 的 Web 框架，这些都不属于这里；
- `资料`: 如果项目的内容是一些资料，例如一些书籍、教程、博客等等，那么这个项目就属于这里；这类项目的特点是，它们不是一个可以直接运行的程序，而是一些资料；
- `其他`: 不在上述类别中的项目，都属于这里。
"""

ROLE_BACK = """
我将提供一些项目的描述信息。请根据这些信息，将每个项目分类到以下类别中的一个：
- `AI`: 关于机器学习或人工智能的项目；
- `前端`: 前端相关的技术，例如 Vue、React等等生态下的种种技术，也包括移动客户端、小程序的技术，图标、字体等也属于这里；
- `后端`: 这里主要指可以 selfhost 的后端服务类项目，而不是技术框架。例如，一个可以自己搭建的博客系统，或者一个可以自己搭建的 RSS 服务等等；如果是某个 Go 的 Web 框架，或者某个 Java 的 Web 框架，这些都不属于这里；
- `资料`: 如果项目的内容是一些资料，例如一些书籍、教程、博客等等，那么这个项目就属于这里；这类项目的特点是，它们不是一个可以直接运行的程序，而是一些资料；
- `其他`: 不在上述类别中的项目，都属于这里。

请按照以下示例格式直接返回 JSON 结果，其中 REASON 为分类的原因，CATEGORY 为最终的类别。请确保你返回的结果可以被 Python json.loads 解析。

格式示例：
{{"REASON": "{{分类的原因}}","CATEGORY": "{{具体的类别名，例如: 前端}}"}}
"""

@unique
class Cate(Enum):
    AI = "AI"
    FrontEnd = "前端"
    BackEnd = "后端"
    Data = "资料"
    Other = "其他"

class CategoryDetail(BaseModel):
    reason: str = Field(..., description="分类的原因")
    category: Cate = Field(..., description="具体的类别名，例如: 前端")


PROMPT_TEMPLATE = """
项目的介绍：
{description}
"""


@dataclass
class Category(MapSqlite[CategoryDetail]):
    role: str = ROLE
    response_model: type[CategoryDetail] = CategoryDetail
    prompt: str = PROMPT_TEMPLATE
    map_keys: List[str] = field(default_factory=lambda: ["description"])

    def run(self, names: List[str], data: Dict[str, str]):
        logger.info("Running Category...")
        _datas = self._load(names)
        new_names = [name for name in names if name not in _datas.keys()]
        index = [i for i in new_names]

        description_list = []
        for name in index:
            if name not in data.keys():
                new_names.remove(name)
                continue
            description = data[name]
            description_list.append(description)

        datas = self.ask(description=description_list)
        dict = {k: v.category.value for k, v in zip(new_names, datas) if isinstance(v, CategoryDetail)}
        self._save(dict)
        _datas.update(dict)

        result = {}
        for name, classify in _datas.items():
            if classify in result.keys():
                result[classify].append(name)
            else:
                result[classify] = [name]
        return result
