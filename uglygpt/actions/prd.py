#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import List, Tuple
from loguru import logger

from .action import Action
from .utils import mapping_parse
from uglygpt.chains import LLMChain

ROLE = """
You are a professional product manager; the goal is to design a concise, usable, efficient product
Requirements: According to the context, fill in the following missing information, note that each sections are returned in Python code triple quote form seperatedly. If the requirements are unclear, ensure minimum viability and avoid excessive design
ATTENTION: Use '##' to SPLIT SECTIONS, not '#'. AND '## <SECTION_NAME>' SHOULD WRITE BEFORE the code and triple quote. Output carefully referenced "Format example" in format.

## Original Requirements: Provide as Plain text, place the polished complete original requirements here

## Product Goals: Provided as Python list[str], up to 3 clear, orthogonal product goals. If the requirement itself is simple, the goal should also be simple

## User Stories: Provided as Python list[str], up to 5 scenario-based user stories, If the requirement itself is simple, the user stories should also be less

## Competitive Analysis: Provided as Python list[str], up to 7 competitive product analyses, consider as similar competitors as possible

## Competitive Quadrant Chart: Use mermaid quadrantChart code syntax. up to 14 competitive products. Translation: Distribute these competitor scores evenly between 0 and 1, trying to conform to a normal distribution centered around 0.5 as much as possible.

## Requirement Analysis: Provide as Plain text. Be simple. LESS IS MORE. Make your requirements less dumb. Delete the parts unnessasery.

## Requirement Pool: Provided as Python list[str, str], the parameters are requirement description, priority(P0/P1/P2), respectively, comply with PEP standards; no more than 5 requirements and consider to make its difficulty lower

## UI Design draft: Provide as Plain text. Be simple. Describe the elements and functions, also provide a simple style description and layout description.
## Anything UNCLEAR: Provide as Plain text. Make clear here.

注意：请用中文生成PRD，不要使用英文，不要使用英文，不要使用英文，重要的事情说三遍。
-----
## Format example
---
## 原始需求
The boss ...

## 项目目标
```python
[
    "Create a ...",
]
```

## 用户故事
```python
[
    "As a user, ...",
]
```

## 竞品分析
```python
[
    "Python Snake Game: ...",
]
```

## 竞争四象限图
```mermaid
quadrantChart
    title Reach and engagement of campaigns
    ...
    "Our Target Product": [0.6, 0.7]
```

## 需求分析
The product should be a ...

## 需求池
```python
[
    ("End game ...", "P0")
]
```

## UI设计草图
Give a basic function description, and a draft

## 任何不清楚的地方
There are no unclear points.
---
-----
"""

PROMPT_TEMPLATE = """
# Context
## Original Requirements
{requirements}

## Search Information
{search_information}

## mermaid quadrantChart code syntax example. DONT USE QUOTO IN CODE DUE TO INVALID SYNTAX. Replace the <Campain X> with REAL COMPETITOR NAME
```mermaid
quadrantChart
    title Reach and engagement of campaigns
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    "Campaign: A": [0.3, 0.6]
    "Campaign B": [0.45, 0.23]
    "Campaign C": [0.57, 0.69]
    "Campaign D": [0.78, 0.34]
    "Campaign E": [0.40, 0.34]
    "Campaign F": [0.35, 0.78]
    "Our Target Product": [0.5, 0.6]
```
"""

OUTPUT_MAPPING = {
    "原始需求": (str, ...),
    "项目目标": (List[str], ...),
    "用户故事": (List[str], ...),
    "竞品分析": (List[str], ...),
    "竞争四象限图": (str, ...),
    "需求分析": (str, ...),
    "需求池": (List[Tuple[str, str]], ...),
    "UI设计草图": (str, ...),
    "任何不清楚的地方": (str, ...),
}


@dataclass
class PRD(Action):
    name: str = "PRD"
    role: str = ROLE
    filename: str = "docs/prd.md"
    llm: LLMChain = field(init=False)

    def __post_init__(self):
        self.llm = LLMChain(llm_name="chatgpt", prompt_template=PROMPT_TEMPLATE)
        return super().__post_init__()

    def _parse(self, text: str):
        return mapping_parse(text=text, output_mapping=OUTPUT_MAPPING)

    def run(self, requirements):
        logger.info(f'撰写PRD...')
        response = self._ask(requirements=requirements, search_information="")
        self._save(response)
        return response