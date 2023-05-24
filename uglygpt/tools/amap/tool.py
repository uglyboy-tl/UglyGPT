"""Tool for the 高德 API."""
import re
from dataclasses import dataclass, field

from uglygpt.tools.base import BaseTool
from uglygpt.utilities.amap import AMap

@dataclass
class AmapRun(BaseTool):
    """Tool that adds the capability to query the Bing search API."""

    name: str = "高德地图"
    description: str = (
        "可以查询某地附近的各类场所的基本信息。"
        "输入的格式为：地点#类型编码。例如：北京中关村#080000|010100."
        "类型编码表如下: 加油站(010100),中餐厅(050100),西餐厅(050200),快餐厅(050300),咖啡馆(050500),茶艺馆(050600),冷饮店(050700),糕饼店(050800),甜品店(050900),商场(060100),便利店(060200),超市(060400),文化用品店(060800),影剧院(080600),旅游景点(110000),科教文化场所(140000),银行(160100)"
    )
    api_wrapper: AMap = field(default_factory=AMap)

    def _run(
        self,
        query: str,
    ) -> str:
        """Use the tool."""
        result = re.match(r"(.*)#(.*)", query)
        if not result:
            return "输入格式错误"
        place_name = result.group(1)
        types = result.group(2).split("|")
        for type in types:
            if not re.search(r"^\d{6}$", type):
                return "输入格式错误"
        place = self.api_wrapper.get(place_name)
        return "\n".join(self.api_wrapper.around(place["location"], types))

if __name__ == "__main__":
    from uglygpt.base import config
    from uglygpt.provider import get_llm_provider
    #config.set_debug_mode(True)

    # Tools
    tools=[AmapRun()]
    # Agent
    from uglygpt.agent.mrkl.base import ZeroShotAgent
    agent = ZeroShotAgent.from_llm_and_tools(tools = tools, llm = get_llm_provider())
    from uglygpt.agent.agent_executor import AgentExecutor
    agent_execution = AgentExecutor(agent = agent, tools = tools)

    # Run
    agent_execution.run("帮我找一找安定门的麦当劳")