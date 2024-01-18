#!/usr/bin/env python3
# -*-coding:utf-8-*-

from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass

from core.llm import get_llm_provider, LLMProvider
from ..base import Chain
from .prompt import Prompt

@dataclass
class LLM(Chain):
    """A class representing an LLM chain.

    This class inherits from the Chain class and implements the logic for interacting with a language model.

    Attributes:
        llm_name: The name of the language model.
        prompt_template: The template for the prompt.
    """
    prompt_template: str = "{prompt}"
    llm_name: str = ""
    role: Optional[str] = None
    memory_callback: Optional[Callable[[Tuple[str,str]],None]] = None

    def __post_init__(self):
        """Initialize the LLMChain object.

        This method initializes the LLMChain object by getting the LLM provider and setting the prompt.
        """
        self._llm = get_llm_provider(self.llm_name)
        if self.role:
            self._llm.set_role(self.role)
        self.prompt = self.prompt_template

    @property
    def input_keys(self) -> List[str]:
        """Get the input keys.

        Returns:
            A list of input keys.
        """
        return self.prompt.input_variables

    def _call(self, inputs: Dict[str, Any]) -> str:
        """Call the LLMChain.

        This method calls the LLMChain by formatting the prompt with the inputs and asking the LLM provider.

        Args:
            inputs: A dictionary of inputs.

        Returns:
            The response from the LLM provider.
        """
        prompt = self.prompt.format(**inputs)
        response = self._llm.ask(prompt)
        if self.memory_callback:
            self.memory_callback((prompt, response))
        return response

    @property
    def prompt(self) -> Prompt:
        """Set the prompt.

        This method sets the prompt using the given prompt template.

        Args:
            prompt_template: The template for the prompt.
        """
        return self._prompt

    @prompt.setter
    def prompt(self, prompt_template: str) -> None:
        """Set the prompt.

        This method sets the prompt using the given prompt template.

        Args:
            prompt_template: The template for the prompt.
        """
        self._prompt = Prompt(prompt_template)

    @property
    def llm(self) -> LLMProvider:
        """Get the LLM provider.

        Returns:
            The LLM provider.
        """
        return self._llm
