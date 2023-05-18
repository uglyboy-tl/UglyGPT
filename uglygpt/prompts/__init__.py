from uglygpt.prompts.base import BasePromptTemplate
from uglygpt.prompts.default import DefaultPromptTemplate

def getPromptTemplate(name: str = None, table_name: str = None):
    match name:
        case _:
            return DefaultPromptTemplate()

__all__ = ["BasePromptTemplate", "getPromptTemplate"]