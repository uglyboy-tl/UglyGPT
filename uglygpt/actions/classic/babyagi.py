#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from loguru import logger
from typing import Deque
from collections import deque
import re

from uglygpt.chains import LLMChain, ReAct, ReActChain
from uglygpt.actions.action import Action


ROLE = """
You are an task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}.
Your response should be a numbered list,
eg: `1. First task\n2. Second task\n3. Third task`
"""

@dataclass
class BabyTasks(ReAct):
    tasks: Deque[str] = field(default_factory=deque)

    def run(self) -> str:
        return "Success"

    @classmethod
    def parse(cls, text: str) -> "BabyTasks":
        result = re.split(r"\d+\.", text)
        tasks = deque([r.strip() for r in result if r.strip()])
        action = tasks.popleft() if tasks else ""
        return BabyTasks(thought=str(tasks), action=action, params={}, tasks=tasks)

    @property
    def done(self) -> bool:
        return len(self.tasks) == 0


    def __str__(self) -> str:
        if self.current:
            context = f"""
The last completed task has the result: {self.obs}.
This result was based on this task description: {self.action}.
These are incomplete tasks: {self.tasks}.
Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks. Use at most 4 steps. Return one task per line in your response."""
        else:
            context = ""
        return context

    @classmethod
    def init(cls) -> "BabyTasks":
        task = "Develop a task list to complete the objective."
        tasks = deque([task])
        return BabyTasks(thought=str(tasks), action=task, params={}, tasks=tasks)

@dataclass
class BabyAGI(Action):
    role: str = ROLE
    objective: str = ""
    llm: LLMChain = field(init=False)

    def __post_init__(self):
        self.role = ROLE.format(objective=self.objective)
        self.llm = ReActChain(llm_name="gpt4", cls = BabyTasks)
        return super().__post_init__()

    def run(self, objective=None):
        logger.info(f'BabyAGI Running ..')
        if objective is not None:
            self.objective = objective
            self.role = ROLE.format(objective=objective)
            super().__post_init__()

        tasks = BabyTasks.init()
        response = self.ask(tasks)
        return response
