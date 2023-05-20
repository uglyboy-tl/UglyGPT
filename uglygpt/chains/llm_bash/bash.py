"""Wrapper around subprocess to run commands."""
from __future__ import annotations

import re
import subprocess
from typing import List, Union
from uuid import uuid4

class BashProcess:
    """Executes bash commands and returns the output."""

    def __init__(
        self,
        strip_newlines: bool = False,
        return_err_output: bool = False,
        persistent: bool = False,
    ):
        """Initialize with stripping newlines."""
        self.strip_newlines = strip_newlines
        self.return_err_output = return_err_output
        self.prompt = ""
        if persistent:
            self.prompt = str(uuid4())

    def run(self, commands: Union[str, List[str]]) -> str:
        """Run commands and return final output."""
        if isinstance(commands, str):
            commands = [commands]
        commands = ";".join(commands)
        return self._run(commands)

    def _run(self, command: str) -> str:
        """Run commands and return final output."""
        try:
            output = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            ).stdout.decode()
        except subprocess.CalledProcessError as error:
            if self.return_err_output:
                return error.stdout.decode()
            return str(error)
        if self.strip_newlines:
            output = output.strip()
        return output

    def process_output(self, output: str, command: str) -> str:
        # Remove the command from the output using a regular expression
        pattern = re.escape(command) + r"\s*\n"
        output = re.sub(pattern, "", output, count=1)
        return output.strip()