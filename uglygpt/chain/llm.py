from typing import Any, Dict, List, Union

from uglygpt.chain.base import Chain
from uglygpt.provider import LLMProvider
from uglygpt.prompts import BasePromptTemplate, getPromptTemplate

class LLMChain(Chain):
    def __init__(self, llm: LLMProvider = None, prompt_name: str = "") -> None:
        self.llm = llm
        self.prompt: BasePromptTemplate = getPromptTemplate(prompt_name)
        self.output_key = "text"

    @property
    def input_keys(self) -> List[str]:
        """Will be whatever keys the prompt expects.

        :meta private:
        """
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        """Will always return text key.

        :meta private:
        """
        return [self.output_key]

    def _execute(self, inputs: Dict[str, Any]) -> str:
        """Execute the chain."""
        prompt = self.prompt.format_prompt(**inputs)
        result = self.llm.instruct(prompt)
        return self.parse_result(result)

    async def _aexecute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.prompt.format_prompt(**inputs)
        result = await self.llm.instruct(prompt)
        return {self.output_key: result}

    def parse_result(
        self, result: str
    ) -> Union[str, List[str], Dict[str, str]]:
        if self.prompt.output_parser is not None:
            return self.prompt.output_parser.parse(result)
        else:
            return {self.output_key: result}