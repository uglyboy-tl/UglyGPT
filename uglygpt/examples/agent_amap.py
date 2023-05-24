from uglygpt.base import config
from uglygpt.provider import get_llm_provider
from uglygpt.tools.amap import AmapRun
#config.set_debug_mode(True)

# Tools
tools=[AmapRun()]
# Agent
from uglygpt.agent.mrkl.base import ZeroShotAgent
agent = ZeroShotAgent.from_llm_and_tools(tools = tools, llm = get_llm_provider())
from uglygpt.agent.agent_executor import AgentExecutor
agent_execution = AgentExecutor(agent = agent, tools = tools)

# Run
agent_execution.run("帮我找一找清华附近比较好的餐厅")