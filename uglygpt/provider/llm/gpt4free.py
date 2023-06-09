from __future__ import annotations
from dataclasses import dataclass, field

import gpt4free
from gpt4free import Provider

from uglygpt.base import config, logger
from uglygpt.provider.llm.base import LLMProvider

@dataclass
class GPT4FreeLLM(LLMProvider):
    requirements: list[str] = field(default_factory= lambda: ["gpt4free"])
    type: str = "useless"

    def instruct(self, prompt: str, tokens: int = 0) -> str:
        if self.type == "useless":
            response = gpt4free.Completion.create(Provider.UseLess, prompt=prompt)
            logger.debug(str(response))
            return response['text']
        # 中国区无法使用
        elif self.type == "you":
            config.start_proxy()
            response = gpt4free.Completion.create(Provider.You, prompt=prompt)
            logger.debug(str(response))
            config.stop_proxy()
            return response['text']
        # 中国区无法使用
        elif self.type == "theb":
            config.start_proxy()
            response = gpt4free.theb.Completion.create(prompt=prompt)
            config.stop_proxy()
            return "".join(response)
        # CouldNotGetAccountException
        elif self.type == "forefront":
            config.start_proxy()
            token = gpt4free.forefront.Account.create(logging=True)
            response = gpt4free.Completion.create(
                Provider.ForeFront, prompt=prompt, model='gpt-4', token=token
            )
            logger.debug(str(response))
            config.stop_proxy()
            return "".join(response)