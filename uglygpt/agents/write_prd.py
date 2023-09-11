from dataclasses import dataclass
from typing import  List, Tuple

from uAgent.base import logger
from uAgent.agents.action import Action
from uAgent.chains.prompt import PromptTemplate
from uAgent.chains.output_parsers.mapping import MappingOutputParser

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
ROLE="""
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
"""
FORMAT_EXAMPLE = """
## Format example
---
## Original Requirements
The boss ...

## Product Goals
```python
[
    "Create a ...",
]
```

## User Stories
```python
[
    "As a user, ...",
]
```

## Competitive Analysis
```python
[
    "Python Snake Game: ...",
]
```

## Competitive Quadrant Chart
```mermaid
quadrantChart
    title Reach and engagement of campaigns
    ...
    "Our Target Product": [0.6, 0.7]
```

## Requirement Analysis
The product should be a ...

## Requirement Pool
```python
[
    ("End game ...", "P0")
]
```

## UI Design draft
Give a basic function description, and a draft

## Anything UNCLEAR
There are no unclear points.
---
-----
"""

OUTPUT_MAPPING = {
    "Original Requirements": (str, ...),
    "Product Goals": (List[str], ...),
    "User Stories": (List[str], ...),
    "Competitive Analysis": (List[str], ...),
    "Competitive Quadrant Chart": (str, ...),
    "Requirement Analysis": (str, ...),
    "Requirement Pool": (List[Tuple[str, str]], ...),
    "UI Design draft":(str, ...),
    "Anything UNCLEAR": (str, ...),
}

@dataclass
class WritePRD(Action):
    name: str = "WritePRD"
    role: str = ROLE
    filename: str = "docs/prd.md"

    def run(self, requirements):
        logger.info(f'Writing PRD..')
        self.llm.set_prompt(PromptTemplate(PROMPT_TEMPLATE + FORMAT_EXAMPLE))
        self._ask(requirements=requirements, search_information="")

    def parse(self):
        prd = self._load()
        output_parser = MappingOutputParser(format_example=FORMAT_EXAMPLE,output_mapping=OUTPUT_MAPPING)
        return output_parser.parse(prd)