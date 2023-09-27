#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import Tuple, List
from queue import Queue

from uglygpt.indexes import DB

@dataclass
class Memory:
    db: DB
    short_term_memory: str = ""
    update_queue: Queue = field(default_factory = Queue)


    def update(self, chat: Tuple[str, str]):
        if self.db is not None:
            self.db.add(chat)
        #llm = LLM("Please summarize past key summary \n<summary>\n {summary} </summary>and new chat_history as follows: <history>\n{history}</history>, around 10 to 20 sentences")
        #memory = llm(summary = self.short_term_memory, history = "\n".join(chat))
        #self.short_term_memory = memory

    def get_long_term_memory(self, query: str, n: int = DB.default_n) -> List[str]:
        return self.db.search(query, n) if self.db is not None else []