from __future__ import annotations
import time
import openai
from dataclasses import dataclass
from colorama import Fore
from openai.error import APIError, RateLimitError

from uglygpt.base import config, logger
from uglygpt.provider.embedding import EmbeddingProvider

openai.api_key = config.openai_api_key
openai.api_base = config.openai_api_base

@dataclass
class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI Embedding provider."""
    model: str = "text-embedding-ada-002"

    def embedding(self, texts:str) -> list:
        """Create an embedding with text-ada-002 using the OpenAI SDK"""
        num_retries = 10
        for attempt in range(num_retries):
            backoff = 2 ** (attempt + 2)
            try:
                return openai.Embedding.create(
                    input=[texts], model=self.model
                )["data"][0]["embedding"]
            except RateLimitError:
                pass
            except APIError as e:
                if e.http_status == 502:
                    pass
                else:
                    raise
                if attempt == num_retries - 1:
                    raise
            logger.error("Error: ", f"API Bad gateway. Waiting {backoff} seconds...")
            time.sleep(backoff)
