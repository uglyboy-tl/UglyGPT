from __future__ import annotations
import openai
import tiktoken
from dataclasses import dataclass, field
from uglygpt.provider.llm.base import LLMProvider
from uglygpt.base import config

# Initialize the OpenAI API client
openai.api_key = config.openai_api_key
openai.api_base = config.openai_api_base

def tiktoken_len(text: str) -> int:
    encoding = tiktoken.encoding_for_model("text-davinci-003")
    return len(
        encoding.encode(text)
    )

@dataclass
class OpenAILLM(LLMProvider):
    """OpenAI LLM provider."""
    requirements: list[str] = field(default_factory= lambda: ["openai"])
    model: str = "text-davinci-003"
    temperature: float = 0.7
    MAX_TOKENS: int = 4096

    def _num_tokens(self, prompt: str) -> int:
        num_tokens = tiktoken_len(prompt)
        return num_tokens

    def instruct(self, prompt: str, tokens: int=None) -> str:
        if tokens is None:
            tokens = self._num_tokens(prompt)
        max_new_tokens = int(self.MAX_TOKENS) - tokens
        if max_new_tokens <= 0:
            raise ValueError(f"Prompt is too long. has {tokens} tokens, max is {self.MAX_TOKENS}")
        completions = openai.Completion.create(
            model=self.model,
            prompt=prompt,
            max_tokens=max_new_tokens,
            temperature=self.temperature,
        )
        message = completions.choices[0].text
        return message
