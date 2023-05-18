import re
from collections import deque
from typing import Dict, List

# Task storage supporting only a single instance of BabyAGI
class TaskListStorage:
    def __init__(self):
        self.tasks = deque([])
        self.task_id_counter = 0
        self.current_task_id = 0
        self.current_task = None
        self.finished_tasks = []
        self.objective = ""

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

    def set_objective(self, objective: str):
        self.objective = objective

