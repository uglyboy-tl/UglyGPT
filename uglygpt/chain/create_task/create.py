import re
from typing import Any, Dict, List

from uglygpt.chain.base import Chain
from uglygpt.chain.llm import LLMChain
from uglygpt.provider import LLMProvider

from uglygpt.agent.task_storage import TaskListStorage
from uglygpt.chain.create_task.prompt import get_prompt

class CreateTaskChain(Chain):
    def __init__(self, llm: LLMProvider = None, tasks: TaskListStorage = None, language: str = "English") -> None:
        self.llm = llm
        self.tasks = tasks
        self.language = language
        self.input_key: str = "result"
        self.output_key: str = "tasks"


    @property
    def _chain_type(self) -> str:
        raise NotImplementedError

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, List]:

        chain = LLMChain(llm = self.llm, prompt = get_prompt("task_creation"))

        new_tasks = chain.parse(task = self.tasks.current_task, objective = self.tasks.objective, tasks = str(self.tasks.get_task_names()), result = inputs[self.input_key], Language = self.language)
        for new_task in new_tasks:
            self.tasks.append({"task_name": new_task})

        task_names = self.tasks.get_task_names()
        if not task_names:
            return

        chain = LLMChain(llm = self.llm, prompt = get_prompt("task_priority"))

        new_tasks = chain.parse(task = str(task_names), objective = self.tasks.objective, Language = self.language)
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

        return {self.output_key: str(self.tasks.get_task_names())}

    # async UnFinished
    def _aexecute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return super()._aexecute(inputs)


from uglygpt.base import logger
from colorama import Fore
from uglygpt.provider import get_llm_provider

if __name__ == "__main__":
    tasks = TaskListStorage()
    tasks.set_objective("在 Macbook 上安装 Debian")

    if tasks.is_empty():
        tasks.append({"task_name":"Develop a task list to complete the objective."})

    while not tasks.is_empty():
        # Show the current tasks
        logger.info(Fore.MAGENTA+f"\nTask List:\n"+Fore.RESET)
        for t in tasks.get_task_names():
            logger.info(Fore.MAGENTA + " • "+ str(t) + Fore.RESET)

        # Get the current task
        tasks.popleft()

        # Execute the task
        task = tasks.current_task["task_name"]
        logger.info(Fore.GREEN+f"\nExecuting task {task}\n"+Fore.RESET)
        result = ""

        # Get New Tasks
        chain = CreateTaskChain(llm = get_llm_provider(), tasks = tasks)
        chain.run(result)