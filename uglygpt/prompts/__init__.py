from __future__ import annotations
from .base import BasePromptTemplate, BaseOutputParser
from .default import PromptTemplate
from .few_shot import FewShotPromptTemplate
from .test import TestPromptTemplate

def getPromptTemplate(name: str = None):
    match name:
        case "test":
            return TestPromptTemplate()
        case _:
            return PromptTemplate(input_variables=["input"], template="{input}")

__all__ = [
    "BasePromptTemplate",
    "BaseOutputParser",
    "PromptTemplate",
    "FewShotPromptTemplate",
    "getPromptTemplate"
]