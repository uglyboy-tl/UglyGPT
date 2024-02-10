from dataclasses import dataclass, field
from typing import List, Dict, TypeVar, Generic, cast
from enum import Enum, unique

from loguru import logger
from pydantic import BaseModel, Field
from uglychain.worker.base import BaseWorker
from uglychain.storage import Storage, SQLiteStorage
from uglychain import MapChain


T = TypeVar("T", bound=Storage)

ROLE = """我将提供一些项目的描述信息。请根据这些信息，将每个项目分类到以下类别中的一个：
- `AI`: 关于机器学习或人工智能的项目；
- `前端`: 前端相关的技术，例如 Vue、React等等生态下的种种技术，也包括移动客户端、小程序的技术，图标、字体等也属于这里；
- `后端`: 这里主要指可以 selfhost 的后端服务类项目，而不是技术框架。例如，一个可以自己搭建的博客系统，或者一个可以自己搭建的 RSS 服务等等；如果是某个 Go 的 Web 框架，或者某个 Java 的 Web 框架，这些都不属于这里；
- `资料`: 如果项目的内容是一些资料，例如一些书籍、教程、博客等等，那么这个项目就属于这里；这类项目的特点是，它们不是一个可以直接运行的程序，而是一些资料；
- `其他`: 不在上述类别中的项目，都属于这里。
"""
PROMPT = """
项目的介绍：
{description}
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


@dataclass
class Category(BaseWorker, Generic[T]):
    role: str = field(init=False, default=ROLE)
    prompt: str = field(init=False, default=PROMPT)
    storage: T = field(default_factory=SQLiteStorage) # type: ignore

    def __post_init__(self):
        self.llm = MapChain(
            self.prompt,
            self.model,
            self.role,
            CategoryDetail,
            map_keys=["description"],
        )

    def run(self, names: List[str], data: Dict[str, str]):
        logger.info("Running Category...")
        _datas = cast(Dict, self.storage.load(names))
        skip_names = set(_datas.keys())
        needin_names = set(data.keys())

        new_names = []
        description_list = []
        for name in names:
            if name in skip_names or name not in needin_names:
                logger.debug(f"Skip {name}")
                continue
            new_names.append(name)
            description_list.append(data[name])

        response = self._ask(description=description_list)
        result = {
            k: v.category.value
            for k, v in zip(new_names, response)
            if isinstance(v, CategoryDetail)
        }
        self.storage.save(result)
        _datas.update(result)

        category_dict = {}
        _ = [category_dict.setdefault(category, []).append(name) for name, category in _datas.items()]

        return category_dict
