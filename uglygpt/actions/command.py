#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from loguru import logger
import subprocess
import platform

from uglygpt.chains import LLMChain, ReAct, ReActChain
from .action import Action
from .utils import parse_json


ROLE = """
你是一名系统运维工程师，你的目标是：`{objective}`。为了完成这个目标，你需要执行一些命令行指令。
- 你需要一步一步的描述你的解决思路，每一步都可以对应一个命令行指令（不要一次执行多个命令）。
    - 你会逐一执行这些指令，并可以根据指令的执行结果来修正下一步的操作。
    - 将已经获得的执行结果融合到你的解决思路中，不断完善你的解决思路。
- 只输出下一步将执行的命令行指令。
    - 确保你的命令行可以自动执行，不需要人工干预。
    - 不要执行切换目录的操作，因为你的命令行指令都只能在特定目录下执行。
    - 因为你能获取的信息有字数限制，所以努力让命令行指令执行的结果精简。
- 请按照 Format example 中的格式直接返回 JSON 结果，其中 `reasoning` 为解决思路，`command` 为即将执行的命令行指令。
    - 确保你返回的结果可以被 Python json.loads 解析。
    - 如果你的目标已完成或者无法解决，则不需要给出命令行指令；

Format example：
{{"reasoning": "{{解决思路}}","command": "{{即将执行的命令行指令，若任务已完成则为空}}"}}
"""

@dataclass
class CommandAct(ReAct):
    def run(self) -> str:
        """Execute a command.

        Args:
            command: The command to execute.

        Returns:
            The output of the command execution.
        """
        command = self.action
        try:
            if platform.system() == "Windows":
                result = subprocess.run(command, shell=True, check=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='powershell')
            else:
                result = subprocess.run('set -o pipefail; ' + command, shell=True, check=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash')
            output = result.stdout.decode().strip()
            if output != "":
                return output
            else:
                return "Command executed successfully."
        except subprocess.CalledProcessError as e:
            logger.warning(e.stderr.decode())
            # raise RuntimeError("Command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            return "Command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output)

    @classmethod
    def parse(cls, text: str) -> "ReAct":
        """Parse the response text.

        Args:
            text: The response text to parse.

        Returns:
            The reasoning and command extracted from the response text.
        """
        result = parse_json(text)
        reason = result.get("reasoning", "")
        command = result.get("command", "")
        return CommandAct(thought=reason, action=command, params={})

    @property
    def done(self) -> bool:
        return self.action == ""

    def __str__(self) -> str:
        if self.current:
            return "## 解决思路：\n" + self.thought + "\n\n## 命令行指令：\n" + \
                "```bash\n" + self.action + "\n```\n\n" + "## 执行结果：\n---" + self.obs + "---\n\n"
        else:
            return ""

@dataclass
class Command(Action):
    """Class representing a command action.

    Attributes:
        role: The role of the system operator engineer.
        objective: The objective of the command action.
        llm: The LLMChain object for language model completion.
    """
    role: str = ROLE
    objective: str = ""
    llm: LLMChain = field(init=False)

    def __post_init__(self):
        """Initialize the Command object.

        Create an ReActChain(LLMChain) object and call the parent class's __post_init__ method.
        """
        self.role = ROLE.format(objective=self.objective)
        self.llm = ReActChain(llm_name="gpt4", cls = CommandAct)
        return super().__post_init__()

    def run(self, objective=None, command=None):
        """Run the command action.

        Args:
            objective: The objective of the command action.
            command: The command to execute.

        Returns:
            None.
        """
        logger.info(f'Command Running ..')
        if objective is not None:
            self.objective = objective
            self.role = ROLE.format(objective=objective)
            super().__post_init__()
        elif command is not None:
            objective = LLMChain(
                llm_name="chatgpt", prompt_template="```bash\n" + command + "\n```"+"请根据上面的命令行指令，执行者的目标是？")()
            logger.debug(f'Objective: {objective}')
            self.objective = objective
            self.role = ROLE.format(objective=objective)
            super().__post_init__()

        response = self.ask()
        logger.success(response)
