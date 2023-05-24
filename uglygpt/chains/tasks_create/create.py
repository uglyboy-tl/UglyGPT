from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

from uglygpt.chains.base import Chain
from uglygpt.chains.llm import LLMChain
from uglygpt.provider import LLMProvider, get_llm_provider

from uglygpt.chains.tasks_create.task_storage import TaskListStorage
from uglygpt.chains.tasks_create.prompt import get_prompt


@dataclass
class CreateTaskChain(Chain):
    """Chain to create a task from a result."""
    tasks: TaskListStorage = field(default_factory=TaskListStorage)
    llm: LLMProvider = field(default_factory=get_llm_provider)
    language: str = "English"
    input_key: str = "result"
    output_key: str = "tasks"

    @property
    def _chain_type(self) -> str:
        raise NotImplementedError

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, str]:

        chain = LLMChain(llm=self.llm, prompt=get_prompt("task_creation"))

        new_tasks = chain.parse(task=self.tasks.current_task, objective=self.tasks.objective, tasks=str(
            self.tasks.get_task_names()), result=inputs[self.input_key], Language=self.language)
        for new_task in new_tasks:
            self.tasks.append({"task_name": new_task})

        task_names = self.tasks.get_task_names()
        if not task_names:
            return

        chain = LLMChain(llm=self.llm, prompt=get_prompt("task_priority"))

        new_tasks = chain.parse(
            task=str(task_names), objective=self.tasks.objective, Language=self.language)
        new_tasks_list = []
        task_id = self.tasks.current_task_id
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_id += 1
                task_name = re.sub(r'[^\w\s_]+', '', task_parts[1]).strip()
                if task_name.strip():
                    new_tasks_list.append({"task_name": task_name})
        if new_tasks_list:
            self.tasks.replace(new_tasks_list)

        return {self.output_key: self.tasks.get_task_names()}


if __name__ == "__main__":
    from uglygpt.base import config, logger, Fore
    from uglygpt.provider import get_llm_provider
    from uglygpt.indexes import get_memory, BaseIndex

    config.debug_mode = True

    tasks = TaskListStorage()
    tasks.set_objective("写一份北京今天的天气预报。")
    memory: BaseIndex = get_memory(config,True)

    if tasks.is_empty():
        tasks.append(
            {"task_name": "Develop a task list to complete the objective."})
        tasks.popleft()
        task = tasks.current_task["task_name"]
        chain = CreateTaskChain(tasks=tasks)
        chain.run("")

    from uglygpt.tools import Tool
    from uglygpt.utilities.bing_search import BingSearchAPIWrapper
    search = BingSearchAPIWrapper(k=5)
    bing = Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events, Search in Chinese."
    )
    tools = [bing]
    prefix = """You are an AI who performs one task based on the following objective: {objective}. Take into account these previously completed tasks: {context}.You have the following commands available to complete this task given."""
    suffix = """Question: {task}
    {agent_scratchpad}"""
    from uglygpt.agent.mrkl.base import ZeroShotAgent
    agent = ZeroShotAgent.from_llm_and_tools(
        tools=tools,
        llm=get_llm_provider(),
        prefix=prefix,
        suffix=suffix,
        input_variables=["objective", "task", "context", "agent_scratchpad"],)
    from uglygpt.agent.agent_executor import AgentExecutor
    agent_execution = AgentExecutor(agent=agent, tools=tools)

    while not tasks.is_empty():
        # Show the current tasks
        logger.info(Fore.MAGENTA+f"\nTask List:\n"+Fore.RESET)
        for t in tasks.get_task_names():
            logger.info(Fore.MAGENTA + " • " + str(t) + Fore.RESET)

        # Get the current task
        tasks.popleft()

        context = memory.get_relevant(tasks.objective,5,"task_name")
        # Execute the task
        task = tasks.current_task["task_name"]
        logger.info(Fore.GREEN+f"\nExecuting task {task}\n"+Fore.RESET)
        result = agent_execution.run(
            objective=tasks.objective, task=task, context="\n".join(context))
        memory.add(result, metadata={"task_name":task})


        # Get New Tasks
        chain = CreateTaskChain(tasks=tasks)
        chain.run(result)