"""Interface for tools."""
from __future__ import annotations
from uglygpt.tools.base import BaseTool, Tool


class InvalidTool(BaseTool):
    """Tool that is run when invalid tool name is encountered by agent."""

    name = "invalid_tool"
    description = "Called when tool name is invalid."

    def _run(
        self, tool_name: str
    ) -> str:
        """Use the tool."""
        return f"{tool_name} is not a valid tool, try another one."

__all__ = ["InvalidTool", "BaseTool", "Tool"]