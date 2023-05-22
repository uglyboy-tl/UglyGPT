from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Optional, Sequence

from uglygpt.tools.base import BaseTool
from uglygpt.prompts import PromptTemplate
from uglygpt.provider import LLMProvider
from uglygpt.chains import LLMChain

from uglygpt.agent.agent import Agent
from uglygpt.agent.schema import AgentOutputParser
from uglygpt.agent.mrkl.prompt import PREFIX, SUFFIX, FORMAT_INSTRUCTIONS
from uglygpt.agent.mrkl.output_parser import MRKLOutputParser

@dataclass
class ZeroShotAgent(Agent):
    output_parser: AgentOutputParser = field(default_factory=MRKLOutputParser)

    @classmethod
    def _get_default_output_parser(cls, **kwargs: Any) -> AgentOutputParser:
        return MRKLOutputParser()

    @property
    def _agent_type(self) -> str:
        """Return Identifier of agent type."""
        return "chat-zero-shot-react-description"
    @property
    def observation_prefix(self) -> str:
        """Prefix to append the observation with."""
        return "Observation: "

    @property
    def llm_prefix(self) -> str:
        """Prefix to append the llm call with."""
        return ""

    @classmethod
    def create_prompt(
        cls,
        tools: Sequence[BaseTool],
        context: str = "",
        prefix: str = PREFIX,
        suffix: str = SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: Optional[List[str]] = None,
    ) -> PromptTemplate:
        """Create prompt in the style of the zero shot agent.

        Args:
            tools: List of tools the agent will have access to, used to format the
                prompt.
            prefix: String to put before the list of tools.
            suffix: String to put after the list of tools.
            ai_prefix: String to use before AI output.
            human_prefix: String to use before human output.
            input_variables: List of input variables the final prompt will expect.

        Returns:
            A PromptTemplate with the template assembled from the pieces here.
        """
        tool_strings = "\n".join([f"> {tool.name}: {tool.description}" for tool in tools])
        tool_names = ", ".join([tool.name for tool in tools])
        format_instructions = format_instructions.format(tool_names=tool_names)
        template = "\n\n".join([prefix, tool_strings, format_instructions, context, suffix])
        if input_variables is None:
            input_variables = ["input", "agent_scratchpad"]
        return PromptTemplate(template=template, input_variables=input_variables)

    @classmethod
    def from_llm_and_tools(
        cls,
        llm: LLMProvider,
        tools: Sequence[BaseTool],
        output_parser: Optional[AgentOutputParser] = None,
        prefix: str = PREFIX,
        suffix: str = SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Agent:
        """Construct an agent from an LLM and tools."""
        cls._validate_tools(tools)
        prompt = cls.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            format_instructions=format_instructions,
            input_variables=input_variables,
        )
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
        )
        tool_names = [tool.name for tool in tools]
        _output_parser = output_parser or cls._get_default_output_parser(
        )
        return cls(
            llm_chain=llm_chain,
            allowed_tools=tool_names,
            output_parser=_output_parser,
            **kwargs,
        )


if __name__ == "__main__":
    from uglygpt.base import config
    from uglygpt.provider import get_llm_provider
    #config.set_debug_mode(True)

    # Tools
    from uglygpt.tools.human import HumanInputRun
    from uglygpt.tools.bing_search import BingSearchRun
    from uglygpt.tools import Tool
    human = HumanInputRun()
    bing = BingSearchRun()

    tools = []
    tools.append(Tool.from_function(lambda x: "张三","找负责人","这个工具可以找到对应项目的负责人是谁"))
    tools.append(Tool.from_function(lambda x: "15120033011","找电话号","这个工具可以找到人名对应的电话号码"))
    tools.append(Tool.from_function(lambda x: "打完了","打电话","这个工具可以给对应的电话号码打电话，需要输入电话号码和电话内容"))
    tools.append(bing)
    tools.append(human)

    # Agent
    from uglygpt.agent.mrkl.base import ZeroShotAgent
    agent = ZeroShotAgent.from_llm_and_tools(tools = tools, llm = get_llm_provider())
    from uglygpt.agent.agent_executor import AgentExecutor
    agent_execution = AgentExecutor(agent = agent, tools = tools)

    # Run
    agent_execution.run("给安全项目的负责人打电话，告知项目完成情况")
    #agent_execution.run("林俊杰的星座")