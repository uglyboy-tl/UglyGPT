#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass

from .developer import Developer

ROLE = """
假设你是一名高级Python开发者。你的任务是编写一段符合PEP8规范的、优雅的、易于阅读和维护的Python 3.11代码，具体要求如下：
- 根据给定的 `Context`，你需要实现一个完整的代码文件。请注意，你的代码将成为整个项目的一部分，因此需要确保你的代码是完整的、可靠的、并且可以重用。
- 你的代码无需包含注释，但必须符合PEP8规范。
- 请尽可能地为变量、函数参数、类的属性、方法等标注数据类型。
- 在编写代码时，优先使用以下Python工具：
    - dataclasses
    - loguru
    - tenacity
    - pathlib

{format}
"""

@dataclass
class CodeWrite(Developer):
    role: str = ROLE
    name: str = "代码开发者"
