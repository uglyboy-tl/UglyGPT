#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from loguru import logger
from typing import Optional

from uglygpt.chains import LLMChain
from uglygpt.utils.merge_docstring import merge_docstring
from ..utils import parse_code
from ..action import Action

ROLE = '''### Requirements
1. Add docstrings to the given code following the google style.
2. Replace the function body with an Ellipsis object(...) to reduce output.
3. If the types are already annotated, there is no need to include them in the docstring.
4. Extract only class, function or the docstrings for the module parts from the given Python code, avoiding any other text.

### Input Example
```python
def function_with_pep484_type_annotations(param1: int) -> bool:
    return isinstance(param1, int)

class ExampleError(Exception):
    def __init__(self, msg: str):
        self.msg = msg
```

### Output Example
```python
def function_with_pep484_type_annotations(param1: int) -> bool:
    """Example function with PEP 484 type annotations.

    Extended description of function.

    Args:
        param1: The first parameter.

    Returns:
        The return value. True for success, False otherwise.
    """
    ...

class ExampleError(Exception):
    """Exceptions are documented in the same way as classes.

    The __init__ method was documented in the class level docstring.

    Args:
        msg: Human readable string describing the exception.

    Attributes:
        msg: Human readable string describing the exception.
    """
    ...
```
'''


@dataclass
class Docstring(Action):
    """Action to add docstrings to code following the google style.

    Attributes:
        name: The name of the action.
        role: The role of the action.
        llm: The LLMChain object.
    """
    name: str = "AddDocstring"
    role: str = ROLE
    llm: LLMChain = field(init=False)

    def __post_init__(self):
        """Initialize the LLMChain object.

        Returns:
            The initialized LLMChain object.
        """
        self.llm = LLMChain(llm_name="chatgpt",
                            prompt_template="```python\n{code}\n```")
        return super().__post_init__()

    def _parse(self, text: Optional[str|None] = None):
        """Parse the given text and merge the docstring with the code.

        Args:
            text: The text to parse.

        Returns:
            The parsed code with merged docstring.
        """
        if text:
            code = parse_code(text)
        else:
            code = self.code
        new_code =  merge_docstring(self.code, code)
        self._save(new_code)
        return new_code

    def run(self, filename: str) -> str:
        """Run the action on the given file.

        Args:
            filename: The name of the file to run the action on.

        Returns:
            The parsed code with merged docstring.
        """
        self.filename = filename
        response = self.ask(self.code)
        return self._parse(response)

    @property
    def code(self):
        """Get the code from the file.

        Returns:
            The code from the file.

        Raises:
            ValueError: If filename is not provided.
        """
        if hasattr(self, "_code"):
            return self._code
        else:
            if self.filename:
                self._code = self._load()
                return self._code
            else:
                raise ValueError("filename is required")