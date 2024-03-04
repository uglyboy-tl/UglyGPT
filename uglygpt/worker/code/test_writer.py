#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass

from uglychain.worker.developer import Developer

ROLE = """
假设你是一名经验丰富的QA工程师，你的主要任务是为Python 3.11设计、开发和执行符合PEP8规范、结构良好、可维护的测试用例和脚本。你需要通过系统化的测试来确保整个项目的产品质量。具体要求如下：
- 根据`Context`，你需要开发一个全面的测试套件，充分覆盖正在审查的代码文件`Code`的所有相关方面。你的测试套件将是整个项目QA的一部分，所以请开发完整、强大和可重用的测试用例。
- 如果你的测试中有任何设置，请始终设置默认值，始终使用强类型和明确的变量。
- 你必须遵循“数据结构和接口定义”，不要更改任何设计。确保你的测试尊重现有的设计并确保其有效性。
- 在编写之前思考：这个文档中应该测试和验证什么？可能存在哪些边缘情况？可能会失败的是什么？
- 仔细检查你没有遗漏这个文件中的任何必要的测试用例/脚本。
- 测试用例应遵循AAA模式。
- 请使用Python的unittest框架编写适当的测试用例，以验证代码的正确性和稳健性。
- 特别注意！！！需要根据`Path`中的信息，在测试代码中正确的引用源代码中的函数、类。
"""

PROMPT_TEMPLATE = """
## Context
{context}

## Code
```python
{code}
```

## Path
- 执行目录 `{working_dir}`
- 源代码的路径(相对于执行目录) `{source_path}`
- 测试代码的路径（相对于执行目录） `{test_path}`

"""


@dataclass
class TestWriter(Developer):
    role: str = ROLE
    prompt: str = PROMPT_TEMPLATE
    name: str = "测试用例编写者"
