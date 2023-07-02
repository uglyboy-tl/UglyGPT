import requests

class ChatGLM:
    def __init__(
        self,
        AI_PROVIDER_URI: str = "http://180.184.83.81:8186",
        AI_MODEL: str = "vicuna",
        chat_key: str = "6aKT1zs0MQunWn0xaaXxW",
        **kwargs,
    ):
        self.requirements = []
        self.AI_PROVIDER_URI = AI_PROVIDER_URI
        self.AI_MODEL = AI_MODEL
        self.chat_key = chat_key

    def instruct(self, prompt: str, tokens: int = 512) -> str:
        response = requests.post(
            self.AI_PROVIDER_URI+"/submit",
            json={"prompt": prompt, "chat_key": self.chat_key},
        )
        return response.json()["response"].replace("\n", "\n")
