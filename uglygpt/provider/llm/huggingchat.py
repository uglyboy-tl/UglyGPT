from hugchat import hugchat

from uglygpt.base import config
from uglygpt.provider.llm.base import LLMProvider

class HuggingChatLLM(LLMProvider):
    def __init__(
        self,
        AI_TEMPERATURE: float = 0.7,
        MAX_TOKENS: int = 2000,
        AI_MODEL: str = "openassistant",
        HUGGINGCHAT_COOKIE_PATH: str = config.workspace_path +"/huggingchat-cookies.json",
        **kwargs,
    ):
        self.requirements = []
        self.AI_TEMPERATURE = AI_TEMPERATURE
        self.MAX_TOKENS = int(MAX_TOKENS)
        self.AI_MODEL = AI_MODEL
        self.HUGGINGCHAT_COOKIE_PATH = HUGGINGCHAT_COOKIE_PATH

    def instruct(self, prompt: str, tokens: int = 512) -> str:
        try:
            chatbot = hugchat.ChatBot(cookie_path=self.HUGGINGCHAT_COOKIE_PATH)
            id = chatbot.new_conversation()
            response = chatbot.chat(
                text=prompt,
                temperature=float(self.AI_TEMPERATURE),
            )
            return response
        except Exception as e:
            print(e)
            return f"HuggingChat Provider Failure: {e}."