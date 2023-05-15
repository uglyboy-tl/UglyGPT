import openai

from uglygpt.provider.llm.base import LLMProvider
from uglygpt.base import config

# Initialize the OpenAI API client
openai.api_key = config.openai_api_key
openai.api_base = config.openai_api_base

class OpenAILLM(LLMProvider):
    def __init__(self):
        self.requirements = ["openai"]
        self.model = "text-davinci-003"
        self.temperature = 0.7
        self.MAX_TOKENS = 4096

    def instruct(self, prompt: str, tokens: int=1024) -> str:
        max_new_tokens = int(self.MAX_TOKENS) - tokens
        completions = openai.Completion.create(
            model=self.model,
            prompt=prompt,
            max_tokens=max_new_tokens,
            temperature=self.temperature,
        )
        message = completions.choices[0].text
        return message
