from time import sleep

import gpt4free
from gpt4free import Provider

from uglygpt.base import config, logger
from uglygpt.provider.llm.base import LLMProvider

class GPT4FreeLLM(LLMProvider):
    def __init__(self,type:str = "useless"):
        self.requirements = ["gpt4free"]
        self.type = type


    def instruct(self, prompt: str, tokens: int = 0) -> str:
        match self.type:
            case "useless":
                response = gpt4free.Completion.create(Provider.UseLess, prompt=prompt)
                logger.debug(str(response))
                return response['text']
            # 中国区无法使用
            case "you":
                config.start_proxy()
                response = gpt4free.Completion.create(Provider.You,prompt="", chat=prompt)
                logger.debug(str(response))
                config.stop_proxy()
                return response.text
            # 中国区无法使用
            case "theb":
                config.start_proxy()
                response = gpt4free.theb.Completion.create(prompt=prompt)
                config.stop_proxy()
                return "".join(response)
            # CouldNotGetAccountException
            case "forefront":
                config.start_proxy()
                token = gpt4free.forefront.Account.create(logging=True)
                response = gpt4free.Completion.create(
                    Provider.ForeFront, prompt=prompt, model='gpt-4', token=token
                )
                logger.debug(str(response))
                config.stop_proxy()
                return "".join(response)

