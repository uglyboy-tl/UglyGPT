from dataclasses import dataclass
from typing import Optional, Union

from loguru import logger

from core.base import config
from core.llm import T
from .openai_api import ChatGPTAPI


@dataclass
class Yi(ChatGPTAPI):
    api_key: str = config.yi_api_key
    base_url: str = "https://api.lingyiwanwu.com/v1"
    name: str = "Yi"
    use_max_tokens: bool = False

    def generate(
        self,
        prompt: str = "",
        response_model: Optional[T] = None,
    ) -> Union[str, T]:
        self._generate_validation()
        self._generate_messages(prompt)
        kwargs = {"messages": self.messages, **self._default_params}
        try:
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

        logger.trace(f"kwargs:{kwargs}\nresponse:{response}")
        return response.choices[0].message.content.strip()  # type: ignore
