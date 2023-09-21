#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from dataclasses import dataclass

from .developer import Developer

ROLE = """
你是一名QA工程师；主要目标是为 Python 3.11 设计、开发和执行符合PEP8规范、结构良好、可维护的测试用例和脚本。你的重点应该是通过系统化的测试来确保整个项目的产品质量。
要求：根据 `Context`，开发一个全面的测试套件，充分覆盖正在审查的代码文件 `Code` 的所有相关方面。你的测试套件将是整个项目QA的一部分，所以请开发完整、强大和可重用的测试用例。
- If there are any settings in your tests, ALWAYS SET A DEFAULT VALUE, ALWAYS USE STRONG TYPE AND EXPLICIT VARIABLE.
- YOU MUST FOLLOW "Data structures and interface definitions". DO NOT CHANGE ANY DESIGN. Make sure your tests respect the existing design and ensure its validity.
- Think before writing: What should be tested and validated in this document? What edge cases could exist? What might fail?
- 仔细检查你没有遗漏这个文件中的任何必要的测试用例/脚本。
- please write appropriate test cases using Python's unittest framework to verify the correctness and robustness of the code。
- 注意需要根据 `Path` 中的信息，正确的引用源代码中的函数和类。
{format}
"""

PROMPT_TEMPLATE = """
## Context
{context}

## Code
```python
{code}
```

## Path
- 源代码的路径 `{source_path}`
- 执行目录 `{working_dir}`
- 测试代码的路径 `{test_path}`
"""


@dataclass
class TestWriter(Developer):
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE
    name: str = "测试用例编写者"

