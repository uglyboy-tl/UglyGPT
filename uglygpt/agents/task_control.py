#!/usr/bin/env python3
#-*-coding:utf-8-*-

from dataclasses import dataclass, field
from collections import deque

from uglygpt.base import logger

from .task_create import TaskCreation
from .task_runner import TaskRunner

@dataclass
class TaskControl:
    objective: str
    task_creater: TaskCreation = None
    task_runner: TaskRunner = field(default_factory=TaskRunner)

    def __post_init__(self):
        self.task_creater = TaskCreation(objective=self.objective)

    def run(self):
        logger.info(f'Task Running ..')
        context = "你系统的基本信息如下：\n" + self.task_runner.system_info + "\n"
        result = self.task_creater.run(context)
        logger.success(result)
        tasks = deque(self.task_creater._parse(result))

        while len(tasks) > 0:
            task = tasks.popleft()
            logger.info(f'Run task: {task}')
            result = self.task_runner.run(task)
            logger.success(result)
            result = self.task_creater.run(tasks, task, result, context)
            logger.success(result)
            tasks = deque(self.task_creater._parse(result))