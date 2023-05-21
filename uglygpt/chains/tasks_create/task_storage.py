from dataclasses import dataclass, field
from collections import deque
from typing import Dict, List

# Task storage supporting only a single instance of BabyAGI
@dataclass
class TaskListStorage:
    """Storage for tasks."""
    tasks: deque = field(default_factory=deque)
    task_id_counter: int = 0
    current_task_id: int = 0
    current_task: Dict = field(default_factory=dict)
    finished_tasks: List[Dict] = field(default_factory=list)
    objective: str = ""

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

