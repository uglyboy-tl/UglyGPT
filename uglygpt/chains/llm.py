from __future__ import annotations
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
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.prompt.format(**inputs)
        if config.debug_mode:
            logger.debug(prompt, "Prompt:\n", Fore.CYAN)
        result = self.llm.instruct(prompt)
        return {self.output_key: result}

    def _parse_result(self, result: str) -> Union[str, List[str], Dict[str, str]]:
        if self.prompt.output_parser is not None:
            return self.prompt.output_parser.parse(result)
        else:
            return result

    def parse(self, callbacks = None, **kwargs: Any) -> str:
        return self._parse_result(self.run(kwargs, callbacks=callbacks))

    def set_prompt(self, prompt: BasePromptTemplate) -> None:
        """Set the prompt template."""
        self.prompt = prompt