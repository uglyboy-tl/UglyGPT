#!/usr/bin/env python3
#-*-coding:utf-8-*-

from dataclasses import dataclass

from .action import Action
from .utils import code_parse, code_running
from uglygpt.base import logger
from uglygpt.chains.prompt import Prompt

ROLE = """
你是一名系统运维工程师，你的工作是通过编写脚本（`{lang}`）来调整系统的配置。对你的具体工作有如下要求：
1. 你的系统的基本信息如下:`{system_info}`。
2. 你需要使用`{lang}`来实现你的需求。
3. 你可以使用系统中已经安装的软件，如果需要，在可能的情况下，你可以安装新的软件。
4. 如果需要更多的权限，请调用系统中的鉴权系统来获取。
5. 如果有需要，可以通过获取用户的输入来获得更多信息。
"""
PROMPT_TEMPLATE = """
-----
# Context
{context}
-----
"""
format_example = """
## Format example
---
## 你的思路
描述解决问题的思路。
## 代码
```{lang}
...
```
---
"""
SYSTEM_INFO = """
import platform
result = platform.system() + ' ' + platform.release() + ' ' + str(platform.freedesktop_os_release())
"""
@dataclass
class TaskRunner(Action):
    role: str = ROLE
    lang: str = "bash"

    def __post_init__(self):
        self.system_info = code_running(SYSTEM_INFO, "python")
        self.role = self.role.format(lang = self.lang, system_info= self.system_info)
        return super().__post_init__()

    def run(self, context) -> str:
        logger.info(f'Writting Code ..')
        self.llm.set_prompt(Prompt(PROMPT_TEMPLATE + format_example.format(lang = self.lang)))
        rp = self._ask(context = context)
        logger.debug(rp)
        code = code_parse(rp, self.lang)
        logger.info(f'Running Code ..')
        result = code_running(code, self.lang)
        return result