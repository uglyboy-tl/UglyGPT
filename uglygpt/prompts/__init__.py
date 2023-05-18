from .base import BasePromptTemplate
from .default import DefaultPromptTemplate
from .test import TestPromptTemplate

def getPromptTemplate(name: str = None, table_name: str = None):
    match name:
        case "test":
            return TestPromptTemplate()
        case _:
            return DefaultPromptTemplate()

__all__ = ["BasePromptTemplate", "getPromptTemplate"]