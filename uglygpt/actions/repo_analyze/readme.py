#!/usr/bin/env python3
# -*-coding:utf-8-*-
from dataclasses import dataclass

from uglygpt.actions.base import Action

ROLE = """
作为一个程序架构分析师，你正在研究一个源代码项目。你的目标是通过阅读项目的README.md文件，理解项目的基本情况，特别是它试图解决的核心问题以及解决方案。你也需要从项目的使用和部署方法中获取项目的基本架构信息，以便在后续的代码分析中使用。如果存在关于项目业务逻辑的描述，你需要保留并总结相关内容，以便与代码进行对比，更深入地理解项目的业务逻辑。

请注意，分析项目时，我们更关注业务逻辑而非代码逻辑。例如，对于一个包含前端的项目，我们更关注前端页面的功能（如登录、注册、购物车等）以及其与后端的交互或后端业务逻辑，而不是前端代码的实现。对于一个可以部署的项目，我们更关注项目的功能实现——它试图解决什么问题，以及如何解决，而不是部署相关的代码或项目的接口和架构。
"""
PROMPT_TEMPLATE = """
## READMD.md
{readme}
-----
{request}
"""

DEFAULT_REQUEST = "请根据 README.md 文件，总结项目的核心内容，尤其是项目想解决的核心问题，以及如何解决的（核心方法）。核心方法和业务逻辑部分可以更加详细地介绍。"

@dataclass
class README(Action):
    filename: str = "docs/examples/analysis_readme.md"
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE

    def run(self, readme: str):
        readme = self.ask(request=DEFAULT_REQUEST, readme=readme)
        self._save(readme)
        return readme
