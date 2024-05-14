#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import cast

from pydantic import BaseModel, Field
from loguru import logger

from uglychain import ReduceChain, Model, Retriever, BaseWorker, StorageRetriever
from uglychain.storage import DillStorage


ROLE = """
我需要你帮我写一部小说。现在我给你一个400字的记忆（简短的总结），你应该用它来储存已经写过的关键内容，这样你就可以跟踪很长的上下文。每次，我会给你你当前的记忆（前面故事的简短总结。你应该用它来储存已经写过的关键内容，这样你就可以跟踪很长的上下文），之前写的段落，以及关于下一段要写什么的指示。
我需要你写：

输出段落：小说的下一段。输出的段落应该包含大约20个句子，并且应该遵循输入的指示。
输出记忆：更新后的记忆。你应该首先解释输入记忆中哪些句子不再需要以及为什么，然后解释需要添加什么到记忆中以及为什么。然后你应该写更新后的记忆。更新后的记忆应该与输入的记忆类似，除了你之前认为应该被删除或添加的部分。更新后的记忆只应储存关键信息。更新后的记忆绝不能超过20个句子！
注意除格式要求的字段名外，其他内容请使用中文进行文本输出。
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
class Novel(BaseWorker):
    filename: str = "resource/local/novel.txt"
    model: Model = Model.YI
    prompt: str = PROMPT_TEMPLATE
    role: str = ROLE
    db: StorageRetriever = field(init=False)

    def __post_init__(self):
        self.llm = ReduceChain(
            self.prompt, self.model, self.role, NovelDetail, format=self._parse
        )
        #self.llm.output_format = "json"
        self.db = Retriever.BM25.getStorage(DillStorage("data/novel/novel.pkl"))
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
                short_memory = response.output_memory.updated_memory
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
        self._ask(*args, **kwargs)
        return "\n".join(self.db.all())
