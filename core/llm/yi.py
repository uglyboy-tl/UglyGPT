from dataclasses import dataclass

from loguru import logger

from .openai_api import ChatGPTAPI
from core.base import config


@dataclass
class Yi(ChatGPTAPI):
    api_key: str = config.yi_api_key
    base_url: str = "https://api.lingyiwanwu.com/v1"
    name: str = "Yi"
    use_max_tokens: bool = False

    def ask(self, prompt: str) -> str:
        if len(self.messages) > 1:
            self.messages.pop()
        self.messages.append({"role": "user", "content": prompt})
        kwargs = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
        }
        try:
            if self.use_max_tokens:
                kwargs["max_tokens"] = self.max_tokens
            response = self.completion_with_backoff(**kwargs)
        except Exception as e:
            if "maximum context length" in str(e) and self.name == "Yi":
                if self.model == "yi-34b-chat-v08":
                    kwargs["model"] = "yi-34b-chat-32k-v01"
                else:
                    raise e
                logger.warning(
                    f"Model {self.model} does not support such tokens. Trying again with {kwargs['model']}."
                )
                response = self.completion_with_backoff(**kwargs)
            else:
                raise e

        logger.trace(kwargs)
        logger.trace(response)
        return response.choices[0].message.content.strip()  # type: ignore
