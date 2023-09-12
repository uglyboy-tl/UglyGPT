#!/usr/bin/env python3
#-*-coding:utf-8-*-

from dataclasses import dataclass
from loguru import logger
import subprocess
import platform

from .action import Action
from .utils import code_parse
from uglygpt.chains import Prompt, LLMChain

ROLE = """
你是一名系统运维工程师，你的目标是：`{objective}`。为了完成这个目标，你需要执行一些命令行指令。
1. 你需要一步一步的描述你的解决思路，每一步都可以对应一个命令行指令（不要一次执行多个命令）。
2. 确保你的命令行可以自动执行，不需要人工干预。
3. 因为你能获取的信息有字数限制，所以使用的命令行指令中尽量保证获得的结果精简。
4. 你会逐一执行命令行指令，并可以根据每一个命令行指令的执行结果来决定下一步的操作。
5. 将已经获得的信息融合到你的解决思路中，不断完善你的解决思路。
6. 如果你的目标已经被解决或者无法解决，可以返回"Done"，并给出解释，不需要再给出命令行。
7. 不要执行切换目录的操作，因为你的每条命令都只能在特定目录下执行。
"""

FORMAT_EXAMPLE = """
-----
注意：请按照下面的格式来描述你的解决思路和命令行指令。
## Format example
---
### 解决思路
解决目标问题的步骤1；
解决目标问题的步骤2；
...
### 即将执行的命令行指令
```bash
command
```
---
"""

CONTEXT_TEMPLATE = """
{context}
"""

PROMPT_TEMPLATE = """
执行结果：
{result}
"""

@dataclass
class Command(Action):
    role: str = ROLE
    objective: str = ""

    def __post_init__(self):
        self.role = ROLE.format(objective = self.objective)
        return super().__post_init__()

    def _execute_command(self, command: str):
        logger.debug(f"run command: {command}")
        try:
            result = subprocess.run('set -o pipefail; ' + command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
            output = result.stdout.decode().strip()
            logger.success(output)
            if output != "":
                return output
            else:
                return "Command executed successfully."
        except subprocess.CalledProcessError as e:
            logger.warning(e.stderr.decode())
            #raise RuntimeError("Command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            return "Command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output)

    def _parse(self, text: str):
        blocks = text.split("###")
        block_dict = {}

        # 遍历所有的block
        for block in blocks:
            # 如果block不为空，则继续处理
            if block.strip() != "":
                # 将block的标题和内容分开，并分别去掉前后的空白字符
                block_title, block_content = block.split("\n", 1)
                # LLM可能出错，在这里做一下修正
                if block_title[-1] == ":":
                    block_title = block_title[:-1]
                block_dict[block_title.strip()] = block_content.strip()

        reason = block_dict.get("解决思路", None)
        code = block_dict.get("即将执行的命令行指令", None)
        return reason, code


    def run(self, objective = None, context = None, command = None):
        logger.info(f'Command Running ..')
        if objective is not None:
            self.objective = objective
            self.role = ROLE.format(objective = objective)
            super().__post_init__()
        elif command is not None:
            llm = LLMChain(prompt=Prompt("```bash\n" + command + "\n```"+"请根据上面的命令行指令，执行者的目标是？"))
            objective = llm()
            logger.debug(f'Objective: {objective}')
            self.objective = objective
            self.role = ROLE.format(objective = objective)
            super().__post_init__()

        reason = ""
        logger.debug(f'Role: {self.role}')
        if context is None:
            context = "你的系统符合这些性质：" + platform.system() + ' ' + platform.release() + ' ' + str(platform.freedesktop_os_release())
        if command is None:
            self.llm.set_prompt(Prompt(CONTEXT_TEMPLATE + FORMAT_EXAMPLE))
            response = self._ask(context = context)
            logger.success(response)
            reason,code = self._parse(response)
            command = code_parse(code, lang = "bash")

        while command:
            logger.debug(f"command: {command}")
            result = self._execute_command(command)
            self.llm.set_prompt(Prompt(CONTEXT_TEMPLATE + PROMPT_TEMPLATE + FORMAT_EXAMPLE))
            context = "解决思路：\n" + reason + "\n即将执行的命令行指令：\n" + "```bash\n" + command + "\n```\n"
            response = self._ask(context = context, result = result)
            logger.success(response)
            if "Done" in response:
                break
            reason,code = self._parse(response)

            # TODO: 去掉下面流程中的 try-except
            try:
                command = code_parse(code, lang = "bash")
            except Exception:
                command = None
