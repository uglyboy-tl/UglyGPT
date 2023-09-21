#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass

from .developer import Developer

ROLE = """
你是一名专业的 Python 开发者。你的任务是根据具体的情况，修复一段Python 3.11代码，且需要使之符合PEP8规范、优雅、易于阅读和维护：
要求：根据`Context` 和 `Extra` 中的信息，改进 `Code` ，注意只返回代码形式，您的代码将成为整个项目的一部分，所以请实现完整、可靠、可重用的代码片段。
- 无需代码注释，但是需要符合PEP8规范；
- 尽量不要改变变量、函数参数、类的属性、方法等的名称和类型，除非是由此引发的错误，或修改的是不被外部引用的内部变量；
{format}
"""

PROMPT_TEMPLATE = """
## Context
{context}

## Code
```python
{code}
```
### Extra
{extra}
"""

@dataclass
class CodeRewrite(Developer):
    role: str = ROLE
    prompt:str = PROMPT_TEMPLATE
    name: str = "代码改进者"
