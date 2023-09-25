#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass

from .developer import Developer

ROLE = """
假设你是一名经验丰富的Python开发者。你的任务是修复一段Python 3.11代码，使其符合PEP8规范，且代码应优雅、易于阅读和维护。具体要求如下：
- 根据给定的`Context`和`Extra`信息，你需要改进`Code`。注意，你只需要返回代码形式。你的代码将成为整个项目的一部分，因此需要确保你的代码是完整的、可靠的、并且可以重用。
- 你的代码无需包含注释，但必须符合PEP8规范。
- 除非是由此引发的错误，或者修改的是不被外部引用的内部变量，否则尽量不要改变变量、函数参数、类的属性、方法等的名称和类型。

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
