#!/usr/bin/env python3
from datetime import datetime
from dataclasses import dataclass

from loguru import logger

from uglychain import LLM
from uglychain.storage import FileStorage

from uglychain.worker.base import BaseWorker
from .schema import TodoItem, TodoItemResponse

ROLE = """You are an AI Assistant that helps you to manage your todo list.
You need to help the user to manager their todo list in todotxt format.

For example:
```plaintext
2023-10-04 一人之下 @电视剧
x (A) 2024-03-03 2024-01-01 换垃圾袋 rec:2m +生活 due:2024-03-01
```

The date format is `YYYY-MM-DD`, and the priority is `(A)`, `(B)`, `(C)`, `(D)`, `(E)`.
The recurrence is `rec:2m`, `rec:1w`, `rec:3d`.
Today is `{today}`.
"""

PROMPT = """Here is my request:
{context}

Help me to translate it into an todo item in todotxt format."""


@dataclass
class Todo(BaseWorker):
    prompt: str = "{context}"
    role: str = ROLE.format(today=datetime.now().strftime("%Y-%m-%d"))
    file_path: str = "data/todotxt/test.txt"

    def __post_init__(self):
        self.llm = LLM(
            self.prompt,
            self.model,
            self.role,
            TodoItemResponse,
        )
        if not self.storage:
            self.storage = FileStorage(self.file_path, append=True)

    def run(self, *args, **kwargs):
        logger.info(f"正在执行 {self.name} 的任务...")
        response = self._ask(*args, **kwargs)
        todo = TodoItem.from_response(response)
        logger.success(str(todo))
        if self.storage:
            self.storage.save(str(todo))
        return str(todo)
