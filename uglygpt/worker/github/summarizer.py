from dataclasses import dataclass, field
from typing import List, TypeVar, Generic, cast, Dict
from loguru import logger
from uglychain.worker.base import BaseWorker
from uglychain.storage import Storage, SQLiteStorage
from uglychain import MapChain

from uglygpt.utilities import GithubAPI

T = TypeVar("T", bound=Storage)

ROLE = """
我在此提供一个 Github 项目的 Readme 文件，我希望你能帮我理解它。请阅读以下的文件内容，并从中提取出该项目的核心价值和主要功能。请注意，我不需要知道关于安装步骤、使用说明等详细信息，而是希望你能以300字以内的简洁语言，给我一个关于项目的核心概念和功能的总结，**注意请使用中文**。
"""
PROMPT = """
项目的描述(可能会对你总结项目有帮助)：
{description}

下面是项目的 Readme 文件：
## READMD.md
{readme}
"""

@dataclass
class ReadmeSummarizer(BaseWorker, Generic[T]):
    role: str = field(init=False, default=ROLE)
    prompt: str = field(init=False, default=PROMPT)
    storage: T = field(default_factory=SQLiteStorage) # type: ignore

    def __post_init__(self):
        self.llm = MapChain(
            self.prompt,
            self.model,
            self.role,
            map_keys=["readme", "description"],
        )

    def run(self, names: List[str], description_list: List[str]):
        logger.info("Running ReadmeSummarizer...")
        _datas = cast(Dict, self.storage.load(names))
        new_names = []
        new_readme_list = []
        new_description_list = []
        skip_names = set(_datas.keys())
        for name, description in zip(names, description_list):
            if name in skip_names:
                logger.debug(f"Skip {name}")
                continue
            readme = GithubAPI.fetch_readme(name)
            if readme is None:
                logger.warning(f"Skip {name}")
                continue
            if len(readme) > 35000:
                readme = readme[:35000]
            new_names.append(name)
            new_readme_list.append(readme)
            new_description_list.append(description)
        response = self._ask(readme=new_readme_list, description=new_description_list)
        result ={}
        for k,v in zip(new_names, response):
            if v == "Error":
                logger.error(f"Error when summarizing {k}")
                continue
            result[k] = v
        self.storage.save(result)
        return result