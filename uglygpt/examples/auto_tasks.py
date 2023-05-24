from uglygpt.base import config, logger, Fore
from uglygpt.provider import get_llm_provider
from uglygpt.indexes import get_memory, BaseIndex
from uglygpt.chains.tasks_create.task_storage import TaskListStorage
from uglygpt.chains.tasks_create.create import CreateTaskChain

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