#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from loguru import logger
from typing import Deque
from collections import deque
import re

from uglygpt.chains import LLM, ReAct, ReActChain
from .base import Action


ROLE = """
You are an task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}.
Your response should be a numbered list,
eg: `1. First task\n2. Second task\n3. Third task`
"""


@dataclass
class BabyTasks(ReAct):
    tasks: Deque[str] = field(default_factory=deque)
    llm: LLM = field(default_factory=LLM)

    def run(self) -> str:
        self.thought = "\n- " + "\n- ".join(self.tasks)
        return self.llm(f"请努力完成如下任务：{self.action}。注意不是让你告诉我解决问题的方法，而是告诉我答案")

    @classmethod
    def parse(cls, text: str) -> "BabyTasks":
        result = re.split(r"\d+\.", text)
        tasks = deque([r.strip() for r in result if r.strip()])
        task = tasks.popleft() if tasks else ""
        return BabyTasks(action=task, tasks=tasks)

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

    @property
    def info(self) -> str:
        if self.done:
            return "[Done] All tasks completed"
        else:
            return f"[Task List]{self.thought}\n[Current Task] {self.action}\n[Task Result] {self.obs}"

    @classmethod
    def init(cls) -> "BabyTasks":
        task = "根据目标生成一个任务列表"
        tasks = deque([task])
        return BabyTasks(action=task, tasks=tasks)


@dataclass
class BabyAGI(Action):
    role: str = ROLE
    objective: str = ""

    def __post_init__(self):
        self.role = ROLE.format(objective=self.objective)
        self.llm = ReActChain(cls=BabyTasks)
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
