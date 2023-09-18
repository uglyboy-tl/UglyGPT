#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import List, Tuple
from loguru import logger

from uglygpt.actions.base import Action
from uglygpt.chains import LLMChain

PROMPT_TEMPLATE = """
## PRD
{PRD}
## API设计文档
{API_Design}
"""
ROLE = '''
你是一位项目经理，目标是根据 PRD 和 API设计文档 来分解任务，给出任务列表，并分析任务依赖性，从更基础的模块开始项目。
根据上下文填充以下缺失的信息，注意所有部分都以Python代码的三引号形式单独返回。这里每个任务的颗粒度是单个文件，如果有任何缺失的文件，你可以补充它们。
注意：使用'##'来分割章节，而不是'#'，并且'## <章节名>'应在代码和三引号之前写。

## 所需的第三方Python包: 以 requirements.txt 的格式提供

## 所需的其他语言第三方包: 以requirements.txt格式提供

## 完整API规范: 使用OpenAPI 3.0，描述前端和后端可能使用的所有API。

## 逻辑分析: 以`Python` list[str, str]形式提供。第一个是文件名，第二个是在此文件中应实现的类/方法/函数。分析文件之间的依赖关系，判断哪些工作应当先完成。

## 任务列表: 以`Python` list[str] 形式提供。每个字符串都是一个文件名，越在前面的，就越是先决依赖，应该优先完成。

## 共享知识: 所有应该公开的事情，比如`utils`函数，`config`中的变量信息等等应该先被明确的内容。

## 任何不清楚的地方: 以纯文本形式描述，确保清晰明确。例如，不要忘记主入口，不要忘记初始化第三方库。
-----
## Format example
---
## 所需的第三方Python包
```python
"""
flask==1.1.2
bcrypt==3.2.0
"""
```

## 所需的其他语言第三方包
```python
"""
没有第三方包 ...
"""
```

## 完整API规范
```python
"""
openapi: 3.0.0
...
description: A JSON object ...
"""
```

## 逻辑分析
```python
[
    ("game.py", "定义了 ..."),
]
```

## 任务列表
```python
[
    "game.py",
]
```

## 共享知识
```python
"""
'game.py' 包含 ...
"""
```

## 任何不清楚的地方
我们需要 ... 如何开始。
---
-----
'''

OUTPUT_MAPPING = {
    "所需的第三方Python包": (str, ...),
    "所需的其他语言第三方包": (str, ...),
    "完整API规范": (str, ...),
    "逻辑分析": (List[Tuple[str, str]], ...),
    "任务列表": (List[str], ...),
    "共享知识": (str, ...),
    "任何不清楚的地方": (str, ...),
}


@dataclass
class TasksSplit(Action):
    name: str = "WriteTasks"
    role: str = ROLE
    filename: str = "docs/examples/subtask.md"
    llm: LLMChain = field(init=False)

    def __post_init__(self):
        self.llm = LLMChain(llm_name="gpt4",
                            prompt_template=PROMPT_TEMPLATE)
        return super().__post_init__()

    def run(self, prd: str, api_design: str):
        logger.info(f'Writing tasks..')
        response = self.ask(PRD=prd, API_Design=api_design)
        self._save(response)
        return response
