from __future__ import annotations
import time
from dataclasses import dataclass,field
from requests.sessions import Session

from uglygpt.provider.llm.base import LLMProvider
from uglygpt.base import config, logger

@dataclass
class HuggingChatLLM(LLMProvider):
    """HuggingChat LLM provider."""
    requirements: list[str] = field(default_factory= lambda: ["requests"])
    AI_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    AI_MODEL: str = "openassistant"
    cookie: str = None

    def instruct(self, prompt: str, tokens: int = 0) -> str:
        self.cookie = config.huggingchat_cookie

        session = Session()
        session.get(url="https://huggingface.co/chat/")
        headers = {"Content-Type": "application/json", "Cookie": self.cookie}
        res = session.post(
            url="https://huggingface.co/chat/conversation",
            json={"model": self._get_model_name(self.AI_MODEL)},
            headers=headers,
        )
        assert res.status_code == 200, "Failed to create new conversation"

        conversation_id = res.json()["conversationId"]
        url = f"https://huggingface.co/chat/conversation/{conversation_id}"
        max_new_tokens = int(self.MAX_TOKENS) - tokens - 428
        res = session.post(
            url=url,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "temperature": float(self.AI_TEMPERATURE),
                    "top_p": 0.95,
                    "repetition_penalty": 1.2,
                    "top_k": 50,
                    "truncate": 1024,
                    "watermark": False,
                    "max_new_tokens": max_new_tokens,
                    "stop": ["<|endoftext|>"],
                    "return_full_text": False,
                },
                "stream": False,
                "options": {"use_cache": False},
            },
            stream=False,
        )
        try:
            data = res.json()
            data = data[0] if data else {}
        except ValueError:
            print(res.text)
            print("Invalid JSON response")
            data = {}
        except:
            if data.get("error_type", None) == "overloaded":
                print(
                    "Provider says that it is overloaded, waiting 3 seconds and trying again"
                )
                # @Note: if this is kept in the repo, the delay should be configurable
                time.sleep(3)
                return self.instruct(prompt)
            else:
                print("Unknown error")
                print(res.text)
                data = {}

        return data.get("generated_text", "")

    def _get_model_name(self, ai_model: str):
        """Returns a model name based on the AI_MODEL"""

        if ai_model == "openassistant":
            model_name = "OpenAssistant/oasst-sft-6-llama-30b-xor"
        elif ai_model == "starcoderbase":
            model_name = "bigcode/starcoder"
        return model_name