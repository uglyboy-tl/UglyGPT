#!/usr/bin/env python3
#-*-coding:utf-8-*-

from typing import Any, Dict, List
from dataclasses import dataclass,field

from uglygpt.llm import LLMProvider, get_llm_provider
from .base import Chain
from .prompt import Prompt

@dataclass
class LLMChain(Chain):
    llm: LLMProvider = field(default_factory=get_llm_provider)
    prompt: Prompt = field(default_factory=Prompt)

    @property
    def input_keys(self) -> List[str]:
        return self.prompt.input_variables

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.prompt.format(**inputs)
        return self.llm.ask(prompt)

    def set_prompt(self, prompt: Prompt) -> None:
        """Set the prompt template."""
        self.prompt = prompt