import platform
from dataclasses import dataclass, field
from typing import List, Type, Union

from uglygpt.tools.base import BaseTool
from uglygpt.utilities.bash import BashProcess

def _get_default_bash_processs() -> BashProcess:
    """Get file path from string."""
    return BashProcess(return_err_output=True)

def _get_platform() -> str:
    """Get platform."""
    system = platform.system()
    if system == "Darwin":
        return "MacOS"
    return system

@dataclass
class ShellTool(BaseTool):
    """Tool to run shell commands."""

    process: BashProcess = field(default_factory=_get_default_bash_processs)
    """Bash process to run commands."""

    name: str = "terminal"
    """Name of tool."""

    description: str = f"Run shell commands on this {_get_platform()} machine."
    """Description of tool."""

    def _run(
        self,
        commands: Union[str, List[str]],
    ) -> str:
        """Run commands and return final output."""
        output, success = self.process.run(commands)
        if not success:
            return f"Error with: {output}"
        return output