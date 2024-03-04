from dataclasses import dataclass
from .base import Todo

@dataclass
class New(Todo):
    name: str = "新建 todo 项"
    file_path: str = "data/todotxt/test.txt"
