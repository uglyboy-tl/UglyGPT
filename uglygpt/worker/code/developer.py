#!/usr/bin/env python3

from dataclasses import dataclass

from pydantic import BaseModel, Field
from loguru import logger
from uglychain import LLM
from uglychain.worker.base import BaseWorker

class CodeType(BaseModel):
    reason: str = Field(..., description="你的思考过程和解决方案")
    code: str = Field(..., description="最终优化后的代码文件中的内容")


PROMPT_TEMPLATE = """
{context}
"""

@dataclass
class Developer(BaseWorker):
    prompt: str = PROMPT_TEMPLATE
    name: str = ""

    def __post_init__(self):
        self.llm = LLM(
            self.prompt,
            self.model,
            f"{self.role}",
            CodeType,
        )

    def run(self, *args, **kwargs):
        logger.info(f"正在执行 {self.name} 的任务...")
        response = self._ask(*args, **kwargs)
        logger.success(response.reason)
        if self.storage:
            self.storage.save(response.code)
        return response