#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from pathlib import Path
from loguru import logger
import subprocess
import platform
from typing import Optional

from core import LLM, ReAct, ReActChain
from workflows.utils import parse_json
from .base import Action

DEBUG = False

ROLE = """
假设你是一名系统运维工程师，你正在操作的系统版本为 {os_version}，你的目标是 {objective}，你当前的目录是 `{cwd}` 。为了达到这个目标，你需要依次执行一系列的命令行指令。请一步步地描述你的解决方案，每一步都应该对应一个命令行指令（请不要在一次操作中执行多个命令）。你需要根据每次指令的执行结果来调整你的下一步操作。请注意，你只能通过命令行来完成你的目标，不能使用图形界面。请将已获得的执行结果融入你的解决方案中，以不断完善你的解决方案。你的输出应该只包含下一步将执行的命令行指令。请确保你的命令能够自动执行，不需要人工干预。如果你的命令行指令需要在特定的目录下执行，请直接给出执行的目录。如果需要执行文件操作，请使用 sed、awk、grep 等命令行工具，或者通过 echo 重定向的方式。因为你能获取的信息有字数限制，所以努力让命令行指令执行的结果尽可能精简。请按照以下示例格式直接返回 JSON 结果，其中 THOUGHT 为解决思路，ACTION 为即将执行的命令行指令，CWD 为命令的执行目录。请确保你返回的结果可以被 Python json.loads 解析。如果你的目标已经完成或无法解决，则不需要给出命令行指令。

格式示例：
{{"THOUGHT": "{{解决思路}}","ACTION": "{{即将执行的命令行指令，若任务已完成则为空}}","CWD": "{{命令的执行目录，this is not required}}"}}
"""
@dataclass
class CommandAct(ReAct):
    def run(self) -> str:
        if self.action == "":
            return "Done"
        """Execute a command.

        Args:
            command: The command to execute.

        Returns:
            The output of the command execution.
        """
        command = str(self.action)
        cwd: Optional[str] = None
        msg = f"即将执行命令：{command}，按 'y' 或 回车 确认，按 'n' 取消："
        if self.params is not None:
            cwd = self.params.get("cwd", "")
            msg = f"即将在目录 '{cwd}' 执行命令：{command}，按 'y' 或 回车 确认，按 'n' 取消："
        # Debug 模式下，需要手动确认执行命令
        if DEBUG and input(msg) not in ["y", ""]:
            return "Command execution cancelled."
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["powershell", "-Command", command], shell=True, check=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
            else:
                result = subprocess.run('set -o pipefail; ' + command, shell=True, check=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable='/bin/bash', cwd=cwd)
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
        reason = result.get("THOUGHT", "")
        command = result.get("ACTION", "")
        cwd = result.get("CWD", "")
        if cwd:
            return CommandAct(thought=reason, action=command, params={"cwd": cwd})
        return CommandAct(thought=reason, action=command)

    @property
    def done(self) -> bool:
        return self.action == ""

    def __str__(self) -> str:
            return f"## THOUGHT：\n{self.thought}\n\n## ACTION：\n```bash\n{self.action}\n```{'(' + self.params['cwd'] + ')' if self.params else ''}\n\n## OBS：\n---\n{self.obs}\n---\n\n"

    @property
    def info(self) -> str:
        if self.done:
            return f"[Thought]: {self.thought}"
        else:
            return f"[Thought]: {self.thought}\n[CMD]: {self.action}{'(' + self.params['cwd'] + ')' if self.params else ''}\n[Result]: {self.obs}"

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
    llm_name: str = "copilot-4"

    def __post_init__(self):
        """Initialize the Command object.

        Create an ReActChain(LLMChain) object and call the parent class's __post_init__ method.
        """
        self.os_version = platform.system()
        if self.os_version == "Linux":
            try:
                self.os_version = platform.freedesktop_os_release()['NAME']
            except:
                pass
        self.role = ROLE.format(objective=self.objective, os_version=self.os_version, cwd=Path.cwd())
        self.llm = ReActChain(llm_name=self.llm_name, role=self.role, cls = CommandAct)
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
        act = None
        if objective is not None:
            self.objective = objective
            self.role = ROLE.format(objective=self.objective, os_version=self.os_version, cwd=Path.cwd())
            self.llm.llm.set_role(self.role)
        elif command is not None:
            objective = LLM()("```bash\n" + command + "\n```"+"请根据上面的命令行指令，执行者的目标是？")
            logger.debug(f'Objective: {objective}')
            self.objective = objective
            self.role = ROLE.format(objective=self.objective, os_version=self.os_version, cwd=Path.cwd())
            act = CommandAct(action=command)
            self.llm.llm.set_role(self.role)

        response = self.ask(act)
        return response
