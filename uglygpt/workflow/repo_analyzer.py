#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
import json

from loguru import logger

from uglygpt.base import File
from uglygpt.actions.repo_analyze import *

@dataclass
class RepoAnalyzer:
    repo_name: str

    def __post_init__(self):
        self.repo = Repo(self.repo_name)
        try:
            self.repo.get()
        except Exception as e:
            logger.error(f"Failed to clone repo {self.repo_name}: {e}")
            raise
        parent = self.repo.path.parent/'repo_analyze'/self.repo.name
        self.repo_info = self.repo.repo_info
        self.blueprint = Blueprint(str(parent/"blueprint.json"))
        self.readme = README(str(parent/"readme.md"))
        self.allcodes = AllCodes(str(parent/"allcodes.json"))

    def analyze(self) -> None:
        logger.info(f"开始分析项目{self.repo_name}")

        logger.info("开始分析项目README.md")
        path = str(self.repo.path)
        doc = File.load(f"{path}/README.md")
        readme = self.readme.run(readme=doc)

        logger.info("开始分析项目目录结构")
        data = self.blueprint.run(path)
        path_dict = dict()
        for item in json.loads(data):
            if item["core"] == 1:
                path_dict[path + "/" + item["path"]] = f"文件所在的目录通常具有如下功能：{item['features']}"

        logger.info("开始分析项目代码")
        self.allcodes.run(path, filter=path_dict, message=readme)

    def conclude(self) -> None:
        logger.info(f"项目{self.repo_name}分析完毕")
        logger.info("开始总结")
        self.display()
        logger.info("总结完毕")

    def display(self) -> None:
        readme = self.readme._load()
        print(readme)
        print("-"*20)
        print(self.repo_info)
        print("-"*20)
        print(self.repo.directory_structure)
        print("-"*20)
        data = self.blueprint._load()
        for item in json.loads(data):
            print(item["path"] + " : " + item["features"])
        print("-"*20)
        analysis = []
        files_analysis = json.loads(self.allcodes._load())
        i = 0
        line = ""
        for k,v in files_analysis.items():
            i += 1
            line_str = f"## `{k}`\n### 代码功能分析\n{v}\n\n"
            print(line_str)
            line += line_str
            if i % 6 == 0:
                analysis.append(line)
                line = ""