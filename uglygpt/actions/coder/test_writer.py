#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from dataclasses import dataclass

from uglygpt.actions.coder.developer import Developer
from uglygpt.actions.utils import parse_json

ROLE = """
你是一名QA工程师；主要目标是为 Python 3.11 设计、开发和执行符合PEP8规范、结构良好、可维护的测试用例和脚本。你的重点应该是通过系统化的测试来确保整个项目的产品质量。
要求：根据上下文，开发一个全面的测试套件，充分覆盖正在审查的代码文件的所有相关方面。你的测试套件将是整个项目QA的一部分，所以请开发完整、强大和可重用的测试用例。
- If there are any settings in your tests, ALWAYS SET A DEFAULT VALUE, ALWAYS USE STRONG TYPE AND EXPLICIT VARIABLE.
- YOU MUST FOLLOW "Data structures and interface definitions". DO NOT CHANGE ANY DESIGN. Make sure your tests respect the existing design and ensure its validity.
- Think before writing: What should be tested and validated in this document? What edge cases could exist? What might fail?
- 仔细检查你没有遗漏这个文件中的任何必要的测试用例/脚本。
- please write appropriate test cases using Python's unittest framework to verify the correctness and robustness of the code:
- 源代码的位置 `{filename}`。源代码和测试代码都直接放在执行目录下，以此为基准，正确的引用源代码中的函数和类。
{format}
"""

PROMPT_TEMPLATE = """
## Context
### 原始需求
{context}
### 源代码
```python
{code}
```
"""


@dataclass
class Test_Writer(Developer):
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE

    def __post_init__(self):
        if self.filename:
            self.role = self.role.format(
                filename=self.filename, format="{format}")
            dir_name = os.path.dirname(self.filename)
            base_name = os.path.basename(self.filename)

            # Create the new file name
            new_name = "text_" + base_name

            # Create the new file path
            self.filename = os.path.join(dir_name, new_name)

        return super().__post_init__()
