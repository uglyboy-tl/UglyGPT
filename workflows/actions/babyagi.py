#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from loguru import logger
from typing import Deque, Optional
from collections import deque

from pydantic import BaseModel

from core import LLM, ReAct, ReActChain
from .base import Action


ROLE = """
You are an task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}.
"""

class TaskList(BaseModel):
    tasks: Deque[str] = field(default_factory=deque)

@dataclass
class BabyTasks(ReAct):
    tasks: Deque[str] = field(default_factory=deque)
    llm: LLM = field(default_factory=LLM)

    def run(self) -> str:
        self.thought = "\n- " + "\n- ".join(self.tasks)
        return self.llm(
            f"请努力完成如下任务：{self.action}。注意不是让你告诉我解决问题的方法，而是告诉我答案"
        )

    @classmethod
    def parse(cls, response: TaskList) -> "BabyTasks":
        tasks = response.tasks
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
Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks. Use at most 4 steps.
请用中文回答。"""
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
    def init(cls, objective: Optional[str]) -> "BabyTasks":
        if objective is None:
            objective = ""
        task = f"根据目标 {objective} 生成一个任务列表"
        tasks = deque([task])
        return BabyTasks(action=task, tasks=tasks)


@dataclass
class BabyAGI(Action):
    role: str = ROLE
    objective: str = ""

    def __post_init__(self):
        self.role = ROLE.format(objective=self.objective)
        self.llm = ReActChain(system_prompt=self.role, reactType=BabyTasks, response_model=TaskList)
        return super().__post_init__()

    def run(self, objective=None):
        logger.info("BabyAGI Running ..")
        if objective:
            self.objective = objective
            self.role = ROLE.format(objective=objective)
            self.llm.llm.set_system_prompt(self.role)
            super().__post_init__()

        tasks = BabyTasks.init(self.objective)
        logger.debug(self.llm.llm.system_prompt)
        response = self.ask(tasks)
        return response
