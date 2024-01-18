#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field

from loguru import logger

from uglygpt import ReduceChain
from agent.indexes import BM25DB
from workflows.utils import parse_json
from ..base import Action

ROLE="""
我需要你帮我写一部小说。现在我给你一个400字的记忆（简短的总结），你应该用它来储存已经写过的关键内容，这样你就可以跟踪很长的上下文。每次，我会给你你当前的记忆（前面故事的简短总结。你应该用它来储存已经写过的关键内容，这样你就可以跟踪很长的上下文），之前写的段落，以及关于下一段要写什么的指示。
我需要你写：

输出段落：小说的下一段。输出的段落应该包含大约20个句子，并且应该遵循输入的指示。
输出记忆：更新后的记忆。你应该首先解释输入记忆中哪些句子不再需要以及为什么，然后解释需要添加什么到记忆中以及为什么。然后你应该写更新后的记忆。更新后的记忆应该与输入的记忆类似，除了你之前认为应该被删除或添加的部分。更新后的记忆只应储存关键信息。更新后的记忆绝不能超过20个句子！

请按照以下示例格式直接返回 JSON 结果，其中 output_paragraph 为输出段落，Rational 为记忆更新的理由，Updated Memory 是更新后的记忆。请确保你返回的结果可以被 Python json.loads 解析。如果你的目标已经完成或无法解决，则不需要给出命令行指令。

格式示例：
{{"output_paragraph": "{{string of output paragraph, around 20 sentences.}}","output_memory": {{"Rational":"{{string that explain how to update the memory}}","Updated Memory": "{{string of updated memory, around 10 to 20 sentences}}"}} }}
"""

PROMPT_TEMPLATE = """
这些是输入：
{history}

## 输入指示：
{input}

-----
现在开始写作，严格按照格式示例中的输出格式组织你的输出。

非常重要！更新后的记忆只应储存关键信息。更新后的记忆绝不能超过500个单词！

非常重要：
你应该首先解释输入记忆中哪些句子不再需要以及为什么，然后解释需要添加什么到记忆中以及为什么。然后，你开始重写输入记忆以获得更新后的记忆。
"""

@dataclass
class Novel(Action):
    filename: str = "docs/examples/novel.txt"
    llm_name: str = "gpt-3.5-turbo-16k"
    prompt: str = PROMPT_TEMPLATE
    role: str = ROLE
    reduce: ReduceChain = field(init=False)
    db: BM25DB = field(init=False)

    def __post_init__(self):
        self.llm = ReduceChain(self.prompt, self.llm_name, format=self._parse)
        self.db = BM25DB("docs/examples/novel.json",True)
        self.db.init()
        return super().__post_init__()

    def _parse(self, response:str) -> str:
        data = parse_json(response)
        short_memory = data.get("output_memory").get("Updated Memory", "")
        input_paragraph = data.get("output_paragraph", "")
        long_memory = self.db.search(input_paragraph, 3)
        input_long_term_memory = '\n'.join(
            [f"相关段落 {i+1} :" + selected_memory for i, selected_memory in enumerate(long_memory)])
        self.db.add(input_paragraph)
        history = f"""## 输入记忆：\n{short_memory}\n\n## 输入段落：\n{input_paragraph}\n\n## 输入相关段落：\n{input_long_term_memory}"""
        return history

    def run(self, *args, **kwargs):
        reponse = self.ask(*args, **kwargs)
        self._parse(reponse)
        return "\n".join(self.db.texts)