from dataclasses import dataclass
from typing import List

from uAgent.base import logger
from uAgent.agents.action import Action
from uAgent.chains.prompt import PromptTemplate
from uAgent.chains.output_parsers.mapping import MappingOutputParser

PROMPT_TEMPLATE = """
# Context
{context}
"""
ROLE = """
你是一名架构师，你的目标是设计一个符合PEP8规范的最先进的Python系统；请充分利用优秀的开源工具。
需求：根据上下文填充以下缺失的信息，注意所有部分都需要以代码形式单独回应。
最大输出：8192个字符或2048个tokens。尽可能使用它们。
注意：使用'##'来分割章节，而不是'#'，并且'## <章节名>'应在代码和三引号之前写。

## 实施方法: 以纯文本的形式描述。分析需求的难点，选择适当的开源框架。

## Python包: 以Python字符串形式提供，内容简洁明了，字符只使用小写和下划线的组合。

## 文件列表: 以`Python`格式 list[str]，只需要编写程序所需的文件列表（越少越好！）。只需要相对路径，需要符合PEP8标准。

## 数据结构和接口定义: 使用`mermaid`的`classDiagram`语法来描述，包括类（包括__init__方法）和函数（带有类型注解），清楚标记类之间的关系，并符合PEP8标准。数据结构应非常详细，API应全面且设计完整。

## 程序调用流程: 使用`mermaid`的`sequenceDiagram`代码语法来描述，需要完整且非常详细，准确使用上文中定义的类和API，覆盖每个对象的CRUD和初始化，语法必须正确。

## 任何不清楚的地方: 以纯文本形式描述，确保清晰明确。
"""
FORMAT_EXAMPLE = """
## Format example
---
## 实施方法
我们将 ...

## Python包
```python
"snake_game"
```

## 文件列表
```python
[
    "main.py",
]
```

## 数据结构和接口定义
```mermaid
classDiagram
    class Game{
        +int score
    }
    ...
    Game "1" -- "1" Food: has
```

## 程序调用流程
```mermaid
sequenceDiagram
    participant M as Main
    ...
    G->>M: end game
```

## 任何不清楚的地方
需求已经都清晰明确了。
---
-----
"""
OUTPUT_MAPPING = {
    "实施方法": (str, ...),
    "Python包": (str, ...),
    "文件列表": (List[str], ...),
    "数据结构和接口定义": (str, ...),
    "程序调用流程": (str, ...),
    "任何不清楚的地方": (str, ...),
}


@dataclass
class WriteDesign(Action):
    name: str = "WriteDesign"
    role: str = ROLE
    filename: str = "docs/design.md"
    desc: str = "Based on the PRD, think about the system design, and design the corresponding APIs, " \
        "data structures, library tables, processes, and paths. Please provide your design, feedback " \
        "clearly and in detail."

    def run(self, context):
        logger.info(f'Writing Design..')
        self.llm.set_prompt(PromptTemplate(PROMPT_TEMPLATE + FORMAT_EXAMPLE))
        self._ask(context=context)

    def parse(self):
        system_design = self._load()
        output_parser = MappingOutputParser(format_example=FORMAT_EXAMPLE,output_mapping=OUTPUT_MAPPING)
        return output_parser.parse(system_design)