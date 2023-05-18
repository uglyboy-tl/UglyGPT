from typing import Any, Dict, List, Union

from uglygpt.chain.base import Chain
from uglygpt.provider import LLMProvider
from uglygpt.prompts import BasePromptTemplate, getPromptTemplate

class LLMChain(Chain):
    def __init__(self, llm: LLMProvider = None, prompt: BasePromptTemplate = None, prompt_name: str = "") -> None:
        self.llm = llm
        if prompt:
            self.prompt = prompt
        else:
            self.prompt = getPromptTemplate(prompt_name)
        self.output_key = "data"

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

    def _execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the chain."""
        prompt = self.prompt.format(**inputs)
        result = self.llm.instruct(prompt)
        return {self.output_key: result}

    async def _aexecute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.prompt.format(**inputs)
        result = await self.llm.instruct(prompt)
        return {self.output_key: result}

    def _parse_result(
        self, result: str
    ) -> Union[str, List[str], Dict[str, str]]:
        if self.prompt.output_parser is not None:
            return self.prompt.output_parser.parse(result)
        else:
            return result

    def parse(self, callbacks = None, **kwargs: Any) -> str:
        """Format prompt with kwargs and pass to LLM.

        Args:
            callbacks: Callbacks to pass to LLMChain
            **kwargs: Keys to pass to prompt template.

        Returns:
            Completion from LLM.

        Example:
            .. code-block:: python

                completion = llm.predict(adjective="funny")
        """
        return self._parse_result(self(kwargs, callbacks=callbacks)[self.output_key])

    def set_prompt(self, prompt: BasePromptTemplate) -> None:
        """Set the prompt template."""
        self.prompt = prompt