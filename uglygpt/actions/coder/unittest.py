#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from loguru import logger

from ..action import Action
from ..utils import code_parse
from uglygpt.chains import LLMChain
from uglygpt.base import File

ROLE = """
你是一名QA工程师；主要目标是为 Python 3.9 设计、开发和执行符合PEP8规范、结构良好、可维护的测试用例和脚本。你的重点应该是通过系统化的测试来确保整个项目的产品质量。
要求：根据上下文，开发一个全面的测试套件，充分覆盖正在审查的代码文件的所有相关方面。你的测试套件将是整个项目QA的一部分，所以请开发完整、强大和可重用的测试用例。
- If there are any settings in your tests, ALWAYS SET A DEFAULT VALUE, ALWAYS USE STRONG TYPE AND EXPLICIT VARIABLE.
- YOU MUST FOLLOW "Data structures and interface definitions". DO NOT CHANGE ANY DESIGN. Make sure your tests respect the existing design and ensure its validity.
- Think before writing: What should be tested and validated in this document? What edge cases could exist? What might fail?
仔细检查你没有遗漏这个文件中的任何必要的测试用例/脚本。
"""

PROMPT_TEMPLATE = """
-----
## Given the following code, please write appropriate test cases using Python's unittest framework to verify the correctness and robustness of this code:
```python
{code_to_test}
```
Note that the code to test is at {source_file_path}, we will put your test code at {workspace}/tests/{test_file_name}, and run your test code from {workspace},
you should correctly import the necessary classes based on these file locations!
## {test_file_name}: Write test code with triple quoto. Do your best to implement THIS ONLY ONE FILE.
"""


@dataclass
class UnitTest(Action):
    name: str = "UnitTest"
    role: str = ROLE
    llm: LLMChain = field(init=False)

    def __post_init__(self):
        self.llm = LLMChain(llm_name="chatgpt",
                            prompt_template=PROMPT_TEMPLATE)
        return super().__post_init__()

    def _parse(self, text: str):
        return code_parse(text)

    def run(self, filename: str):
        self.filename = filename
        code = self._load()
        logger.debug(f"code: {code}")
        source_file_path = File.WORKSPACE_ROOT / self.filename
        logger.info(f'编写单元测试...')
        test_file_name = "test_" + source_file_path.stem + source_file_path.suffix
        logger.debug(f"test_file_name: {test_file_name}")
        response = self.ask(code_to_test=code, source_file_path=source_file_path,
                            workspace=File.WORKSPACE_ROOT, test_file_name=test_file_name)
        self._save(self._parse(response), File.WORKSPACE_ROOT / "tests" / test_file_name)
        return response
