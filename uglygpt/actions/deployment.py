#!/usr/bin/env python3
#-*-coding:utf-8-*-

from dataclasses import dataclass
from loguru import logger
import subprocess
import re

from .action import Action
from .command import Command

ROLE = """
你是一名系统运维工程师，你将根据文档，在 `{deploy_path}` 完成一个项目的部署。
你需要将文档中的步骤拆解成任务列表，并完成这些任务，部分要求如下：
- 任务列表中，每一个任务都可以对应一个命令行指令（不要一次执行多个命令）。
- 确保你的命令行可以自动执行，不需要人工干预。
- 因为你能获取的信息有字数限制，所以使用的命令行指令中尽量保证获得的结果精简。
- 你会逐一执行命令行指令，若指令执行失败会有其他人帮助你修复错误，确保任务完成。
- 你的每条命令都只能在特定目录下执行，所以不要执行切换目录操作，而是直接带路径执行。
- 如果需要执行项目中的脚本，请调用终端来执行，例如 `x-terminal-emulator -e script.sh`。
- 请按照 Format example 的格式来描述你的解决思路和命令行指令。
-----
## Format example
---
## 任务列表
- 任务1: 描述; 命令: `command1`
- 任务2: 描述; 命令: `command2`
...
---
"""

PROMPT_TEMPLATE = """
## 安装指南
{context}
"""

@dataclass
class Deployment(Action):
    role: str = ROLE
    deploy_path: str = ""

    def __post_init__(self):
        # 初始化 Role
        self.role = ROLE.format(deploy_path = self.deploy_path)
        # 初始化 Prompt
        self.llm.prompt = PROMPT_TEMPLATE
        return super().__post_init__()

    def _parse(self, result: str):
        lists = result.split("\n")
        pattern = r'\s*-\s*(.*?):(.*?);(.*?):\s*`(.*?)`'
        tasks = []
        for list in lists:
            pattern_match = re.search(pattern, list)
            if pattern_match:
                name = pattern_match.groups()[1]
                code = pattern_match.groups()[3]
                tasks.append({"name":name, "code":code})
        return tasks

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
            raise RuntimeError("Command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            #return "Command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output)

    def run(self, context = ""):
        response = self._ask(context = context)
        tasks = self._parse(response)
        logger.success(tasks)
        for task in tasks:
            try:
                result = self._execute_command(task["code"])
            except:
                command = Command(objective = task["name"])
                result = command.run(command=task["code"])
            logger.success(result)