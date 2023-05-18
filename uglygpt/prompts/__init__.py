from .base import BasePromptTemplate
from .default import PromptTemplate
from .test import TestPromptTemplate

def getPromptTemplate(name: str = None, table_name: str = None):
    match name:
        case "test":
            return TestPromptTemplate()
        case _:
            return PromptTemplate(input_variables=["input"], template="{input}")

__all__ = ["BasePromptTemplate", "getPromptTemplate"]