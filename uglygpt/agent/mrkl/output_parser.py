from __future__ import annotations
import re
from typing import Union

from uglygpt.agent.agent import AgentOutputParser
from uglygpt.agent.mrkl.prompt import FORMAT_INSTRUCTIONS
from uglygpt.agent.schema import AgentAction, AgentFinish
from uglygpt.prompts import OutputParserException

FINAL_ANSWER_ACTION = "Final Answer:"
OBSERVATION_PREFIX = "Observation:"
class MRKLOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if FINAL_ANSWER_ACTION in text:
            return AgentFinish(
                {"output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}, text
            )
        # \s matches against tab/newline/whitespace
        text = text.split(OBSERVATION_PREFIX)[0].strip()
        regex = (
            r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        )
        match = re.search(regex, text, re.DOTALL)
        if not match:
            raise OutputParserException(f"Could not parse LLM output: `{text}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        return AgentAction(action, action_input.strip(" ").strip('"'), text)

    @property
    def _type(self) -> str:
        return "mrkl"