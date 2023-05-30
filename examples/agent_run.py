from uglygpt.base import config
from uglygpt.provider import get_llm_provider

#config.set_debug_mode(True)

# Tools
from uglygpt.tools.human import HumanInputRun
from uglygpt.tools.bing_search import BingSearchRun
#from uglygpt.tools.arxiv import ArxivQueryRun
from uglygpt.tools import Tool

human = HumanInputRun()
bing = BingSearchRun()
#arxiv = ArxivQueryRun()

tools = []
#tools.append(Tool.from_function(lambda x: "张三","找负责人","这个工具可以找到对应项目的负责人是谁"))
#tools.append(Tool.from_function(lambda x: "15120033011","找电话号","这个工具可以找到人名对应的电话号码"))
#tools.append(Tool.from_function(lambda x: "打完了","打电话","这个工具可以给对应的电话号码打电话，需要输入电话号码和电话内容"))
tools.append(bing)
#tools.append(human)
#tools.append(arxiv)

# Agent
from uglygpt.agent.mrkl.base import ZeroShotAgent

agent = ZeroShotAgent.from_llm_and_tools(tools = tools, llm = get_llm_provider())

from uglygpt.agent.agent_executor import AgentExecutor

agent_execution = AgentExecutor(agent = agent, tools = tools)

# Run
#agent_execution.run("给安全项目的负责人打电话，告知项目完成情况")
agent_execution.run("林俊杰的星座")
#agent_execution.run("给我一些关于 MRKL System 的信息")