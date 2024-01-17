from openai import OpenAI
from .chatgpt import ChatGPT

from uglygpt.base import config

class Copilot(ChatGPT):
    client: OpenAI = OpenAI(api_key=config.copilot_token, base_url=config.copilot_gpt4_service_url)
    name: str = "Github Copilot"
    use_max_tokens: bool = False