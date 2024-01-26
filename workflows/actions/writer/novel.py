#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import cast

from pydantic import BaseModel, Field
from loguru import logger

from core import ReduceChain, Model
from agent.retrievers import StoresRetriever, get_stores_retriever
from ..base import Action

ROLE = """
我需要你帮我写一部小说。现在我给你一个400字的记忆（简短的总结），你应该用它来储存已经写过的关键内容，这样你就可以跟踪很长的上下文。每次，我会给你你当前的记忆（前面故事的简短总结。你应该用它来储存已经写过的关键内容，这样你就可以跟踪很长的上下文），之前写的段落，以及关于下一段要写什么的指示。
我需要你写：

输出段落：小说的下一段。输出的段落应该包含大约20个句子，并且应该遵循输入的指示。
输出记忆：更新后的记忆。你应该首先解释输入记忆中哪些句子不再需要以及为什么，然后解释需要添加什么到记忆中以及为什么。然后你应该写更新后的记忆。更新后的记忆应该与输入的记忆类似，除了你之前认为应该被删除或添加的部分。更新后的记忆只应储存关键信息。更新后的记忆绝不能超过20个句子！
注意除格式要求的字段名外，其他内容请使用中文进行文本输出。
"""
"""
请按照以下示例格式直接返回 JSON 结果，其中 output_paragraph 为输出段落，Rational 为记忆更新的理由，Updated Memory 是更新后的记忆。请确保你返回的结果可以被 Python json.loads 解析。如果你的目标已经完成或无法解决，则不需要给出命令行指令。

格式示例：
{{"output_paragraph": "{{string of output paragraph, around 20 sentences.}}","output_memory": {{"Rational":"{{string that explain how to update the memory}}","Updated Memory": "{{string of updated memory, around 10 to 20 sentences}}"}} }}
"""


class OutputMemory(BaseModel):
    rational: str = Field(
        ..., description="string that explain how to update the memory"
    )
    updated_memory: str = Field(
        ..., description="string of updated memory, around 10 to 20 sentences"
    )


class NovelDetail(BaseModel):
    output_paragraph: str = Field(
        ..., description="string of output paragraph, around 20 sentences."
    )
    output_memory: OutputMemory


PROMPT_TEMPLATE = """
这些是输入：
{history}

## 输入指示：
{input}

-----
"""


@dataclass
class Novel(Action):
    filename: str = "resource/local/novel.txt"
    model: Model = Model.GPT3_TURBO_16K
    prompt: str = PROMPT_TEMPLATE
    role: str = ROLE
    reduce: ReduceChain = field(init=False)
    db: StoresRetriever = field(init=False)

    def __post_init__(self):
        self.llm = ReduceChain(
            self.prompt, self.model, self.role, NovelDetail, format=self._parse
        )
        self.db = get_stores_retriever("bm25", "resource/local/novel.json", True)
        self.db.init()
        return super().__post_init__()

    def _parse(self, response: str | NovelDetail) -> str:
        if response == "":
            input_paragraph = ""
            short_memory = ""
        else:
            try:
                response = cast(NovelDetail, response)
                input_paragraph = response.output_paragraph
                short_memory = response.output_memory.rational
            except Exception:
                logger.error(f"Response is not NovelDetail, can not parse. {response}")
                raise ValueError("Response is not NovelDetail, can not parse.")
        long_memory = self.db.search(input_paragraph, 3)
        input_long_term_memory = "\n".join(
            [
                f"相关段落 {i+1} :" + selected_memory
                for i, selected_memory in enumerate(long_memory)
            ]
        )
        self.db.add(input_paragraph)
        history = f"""## 输入记忆：\n{short_memory}\n\n## 输入段落：\n{input_paragraph}\n\n## 输入相关段落：\n{input_long_term_memory}"""
        return history

    def run(self, *args, **kwargs):
        reponse = self.ask(*args, **kwargs)
        self._parse(reponse)
        return "\n".join(self.db.all())
