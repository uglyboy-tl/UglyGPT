import re
from collections import deque
from typing import Dict, List
from colorama import Fore

from uglygpt.provider import get_llm_provider, LLMProvider
from uglygpt import logger
from uglygpt.agent.prompt import AgentPrompt

# Task storage supporting only a single instance of BabyAGI
class TaskListStorage:
    def __init__(self):
        self.tasks = deque([])
        self.task_id_counter = 0
        self.current_task_id = 0
        self.current_task = None
        self.finished_tasks = []

    def append(self, task: Dict):
        self.tasks.append(task)

    def replace(self, tasks: List[Dict]):
        self.tasks = deque(tasks)

    def popleft(self):
        self.current_task_id += 1
        self.current_task = self.tasks.popleft()
        self.finished_tasks.append(self.current_task)
        return self.current_task

    def is_empty(self):
        return False if self.tasks else True

    def next_task_id(self):
        self.task_id_counter += 1
        return self.task_id_counter

    def get_task_names(self):
        return [t["task_name"] for t in self.tasks]

format_prompt = AgentPrompt()

def _validate_task_list(response):
    lines = response.split("\n") if "\n" in response else [response]
    new_tasks = [
        re.sub(r"^.*?(\d)", r"\1", line)
        for line in lines
        if line.strip() and re.search(r"\d", line[:10])
    ] or [response]
    return new_tasks

def task_creation(result: Dict, tasks: TaskListStorage, llm: LLMProvider = get_llm_provider("huggingchat")):
    prompt = format_prompt("task", result=result, task=tasks.current_task, tasks=tasks.get_task_names())
    response = llm.instruct(prompt)
    new_tasks = _validate_task_list(response)
    for new_task in new_tasks:
        tasks.append({"task_name": new_task})

    task_names = tasks.get_task_names()
    if not task_names:
        return
    prompt = format_prompt("priority", task=str(task_names))
    response = llm.instruct(prompt)
    new_tasks = _validate_task_list(response)
    new_tasks_list = []
    task_id = tasks.current_task_id
    for task_string in new_tasks:
        task_parts = task_string.strip().split(".", 1)
        if len(task_parts) == 2:
            task_id += 1
            task_name = re.sub(r'[^\w\s_]+', '', task_parts[1]).strip()
            if task_name.strip():
                new_tasks_list.append({"task_name": task_name})
    if new_tasks_list:
        tasks.replace(new_tasks_list)

if __name__ == "__main__":
    format_prompt.set_objective("在 Macbook 上安装 Debian")
    tasks = TaskListStorage()

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
        result = {"data":""}

        # Get New Tasks
        task_creation(result, tasks)
