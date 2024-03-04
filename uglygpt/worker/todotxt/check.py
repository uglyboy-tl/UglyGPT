from dataclasses import dataclass
from loguru import logger
from .base import Todo
from .schema import TodoItem

PROMPT = """Here is my todo-txt:
```plaintext
{todo}
```

now I have some more information:
{context}

Please help me to check whether the todo item is needed to be changed.
Please response original todo items that you think is needed to be changed.
"""

@dataclass
class Check(Todo):
    name: str = "检查 todo 项"
    file_path: str = "data/todotxt/todo.txt"
    prompt: str = PROMPT

    def run(self, context:str):
        logger.info(f"正在执行 {self.name} 的任务...")
        response = self._ask(todo=self._read(), context=context)
        for line in response.split("\n"):
            logger.debug(line)
            todo = TodoItem.from_todostr(line)

