from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any

from uglygpt.base import config, logger
from uglygpt.chains.base import Chain
from uglygpt.chains.llm import LLMChain
from uglygpt.chains.novel.init_prompt import InitPromptTemplate
from uglygpt.chains.novel.plan_prompt import PlanPromptTemplate
from uglygpt.chains.novel.prepare_prompt import PreparePromptTemplate
from uglygpt.chains.novel.prompt import NovelPromptTemplate
from uglygpt.prompts import BasePromptTemplate

@dataclass
class NovelChain(Chain):
    llm_chain: LLMChain = field(default_factory=LLMChain)
    """[Deprecated] LLM wrapper to use."""
    prompt: BasePromptTemplate = field(default_factory=InitPromptTemplate)
    """[Deprecated] Prompt to use to translate to python if necessary."""
    #memory: BaseIndex = field(default_factory=lambda: get_memory(config,True))

    @property
    def input_keys(self) -> List[str]:
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        return self.prompt.output_parser.output_variables

    def set_type(self, type):
        if type == "novel":
            self.prompt = PreparePromptTemplate()
        elif type == "plan":
            self.prompt = PlanPromptTemplate()
        elif type == "init":
            self.prompt = InitPromptTemplate()
        else:
            self.prompt = NovelPromptTemplate()
        self.llm_chain.set_prompt(self.prompt)

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        response = self.llm_chain(inputs)
        if config.debug_mode:
            logger.debug(response,"Response from LLM")
        return self.prompt.output_parser.parse(response[self.llm_chain.output_keys[0]])