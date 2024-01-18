#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
import json

from loguru import logger

from .utils import File
from uglygpt.chains import LLM
from .actions.repo_analyze import *

FORMAT_EXAMPLE = """
# <项目名称>
## 项目背景
<介绍项目要解决的问题，和使用的核心解决手段，以及其他一些重要的跟项目相关的信息>
## 项目状况
<介绍项目的当前状况，包括项目网址、项目使用的编程语言、标签、最近更新时间，最近更新次数，项目的 Star 数、Fork 数、讨论数等等各种信息，我们掌握的跟项目整体状况有关的信息都可以在这里列出来>
## 项目结构
<介绍项目的整体结构，包括项目主要的文件、主要的函数、主要的类等等，这部分可以用 markdown 表格的形式来展现>
"""

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
        self.allcodes = AllCodes(str(parent/"allcodes.json"), table=self.repo_name)
        self.conclusion = Conclusion(str(parent/"conclusion.md"))

    def analyze(self) -> None:
        logger.info(f"开始分析项目{self.repo_name}")

        logger.info("开始分析项目README.md")
        path = str(self.repo.path)
        doc = File.load(f"{path}/README.md")
        readme = self.readme.run(readme=doc)

        logger.info("开始分析项目目录结构")
        data = self.blueprint.run(path)

        logger.info("开始分析项目代码")
        path_dict = dict()
        for item in json.loads(data):
            if item["core"] == 1:
                path_dict[path + "/" + item["path"]] = f"文件所在的目录通常具有如下功能：{item['features']}"
        self.allcodes.run(path, filter=path_dict, message=readme)

        logger.info(f"项目 {self.repo_name} 分析完毕")

    def conclude(self) -> None:
        logger.info("开始总结")
        info = self.readme._load() + "\n" + str(self.repo_info) + "\n" + self.blueprint._load()
        llm = LLM(f"请将下列信息整理成示例格式的分析报告。\n信息如下：\n```\n{{info}}```\n示例格式如下：{FORMAT_EXAMPLE}\n\n","chatgpt-16k")
        report = llm(info=info)

        logger.debug(report)

        """ analysis = []
        i = 0
        line = ""
        for k,v in json.loads(self.allcodes._load()).items():
            i += 1
            line_str = f"## `{k}`\n### 代码功能分析\n{v}\n\n"
            line += line_str
            if i % 6 == 0:
                analysis.append(line)
                line = ""
        self.conclusion.run(analysis=analysis, history=report, format=FORMAT_EXAMPLE) """