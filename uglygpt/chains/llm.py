from typing import Any, Dict, List, Union
from dataclasses import dataclass,field

from colorama import Fore
from uglygpt.base import config, logger

from uglygpt.chains.base import Chain
from uglygpt.provider import LLMProvider, get_llm_provider
from uglygpt.prompts import BasePromptTemplate, getPromptTemplate

@dataclass
class LLMChain(Chain):
    llm: LLMProvider = field(default_factory=get_llm_provider)
    prompt: BasePromptTemplate = field(default_factory=getPromptTemplate)
    output_key: str = "data"

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

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the chain."""
        prompt = self.prompt.format(**inputs)
        if config.debug_mode:
            logger.debug(prompt, "Prompt:\n", Fore.CYAN)
        result = self.llm.instruct(prompt)
        return {self.output_key: result}

    def predict(self, callbacks = None, **kwargs: Any) -> str:
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
        return self(kwargs, callbacks=callbacks)[self.output_key]

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