#!/usr/bin/env python3
#-*-coding:utf-8-*-

from typing import Any, Dict, List
from dataclasses import dataclass,field

from uglygpt.llm import get_llm_provider
from .base import Chain
from .prompt import Prompt

@dataclass
class LLMChain(Chain):
    llm_name: str = "gpt4"
    prompt_template: str = ">>> {prompt}"

    def __post_init__(self):
        self.llm = get_llm_provider(self.llm_name)
        self.prompt = self.prompt_template

    @property
    def input_keys(self) -> List[str]:
        return self.prompt.input_variables

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.prompt.format(**inputs)
        return self.llm.ask(prompt)

    @property
    def prompt(self) -> Prompt:
        return self._prompt

    @prompt.setter
    def prompt(self, prompt_template: str) -> None:
        self._prompt = Prompt(prompt_template)