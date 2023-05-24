from dataclasses import dataclass, field
from typing import Any, Dict, List
from io import BytesIO
import os.path
import uuid
from base64 import b64decode
import openai
import requests
from PIL import Image

from uglygpt.base import config, logger, Fore
from uglygpt.chains.base import Chain
from uglygpt.chains.llm import LLMChain
from uglygpt.provider import LLMProvider, get_llm_provider
from uglygpt.chains.gen_image.prompt import PROMPT, BasePromptTemplate
from uglygpt.chains.gen_image.prompt import ALL

@dataclass
class ImageGeneratorChain(Chain):
    HUGGINGFACE_API_TOKEN:str = config.huggingface_api_token
    OPENAI_API_KEY:str = config.openai_api_key
    llm_chain: LLMChain = field(default_factory=LLMChain)
    output_key: str = "result"

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return self.llm_chain.input_keys

    @property
    def output_keys(self) -> List[str]:
        """Expect output key.

        :meta private:
        """
        return [self.output_key]

    def _call(
        self,
        inputs: Dict[str, str],
    ) -> Dict[str, str]:
        prompt = self.llm_chain.run(inputs[self.input_keys[0]])
        logger.debug(prompt, "Prompt:\n", Fore.CYAN)
        prompt_type = ""
        if prompt_type in ALL.keys():
            prompt = ALL[prompt_type.strip()]
            prompt = prompt.replace("{Prompt}", prompt)
        return self.generate_image(prompt.split("\"")[1])

    def generate_image(self, prompt: str) -> str:
        filename = f"{str(uuid.uuid4())}.jpg"

        if self.HUGGINGFACE_API_TOKEN:
            result = self.generate_image_with_hf(prompt, filename)
        elif self.OPENAI_API_KEY:
            result = self.generate_image_with_dalle(prompt, filename)
        else:
            result = "No Image Provider Set"
        return {self.output_key: result}

    def generate_image_with_hf(self, prompt: str, filename: str) -> str:
        API_URL = (
            #"https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            #"https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        )
        headers = {"Authorization": f"Bearer {self.HUGGINGFACE_API_TOKEN}"}

        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": prompt,
            },
        )

        image = Image.open(BytesIO(response.content))
        print(f"Image Generated for prompt:{prompt}")

        image.save(os.path.join(config.workspace_path, filename))

        return f"Saved to disk:{filename}"

    def generate_image_with_dalle(self, prompt: str, filename: str) -> str:
        openai.api_key = self.OPENAI_API_KEY

        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="b64_json",
        )

        print(f"Image Generated for prompt:{prompt}")

        image_data = b64decode(response["data"][0]["b64_json"])

        with open(f"{config.workspace_path}/{filename}", mode="wb") as png:
            png.write(image_data)

        return f"Saved to disk:{filename}"

    @classmethod
    def from_llm(
        cls,
        llm: LLMProvider = get_llm_provider(),
        prompt: BasePromptTemplate = PROMPT,
        **kwargs: Any,
    ) -> Chain:
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        return cls(llm_chain=llm_chain, **kwargs)