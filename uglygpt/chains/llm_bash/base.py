"""Chain that interprets a prompt and executes bash code to perform bash operations."""
from __future__ import annotations
from dataclasses import dataclass, field

from typing import Any, Dict, List

from uglygpt.base import logger, Fore
from uglygpt.provider.llm import LLMProvider
from uglygpt.chains.base import Chain
from uglygpt.chains.llm import LLMChain
from uglygpt.chains.llm_bash.prompt import PROMPT
from uglygpt.prompts import BasePromptTemplate, OutputParserException
from uglygpt.chains.llm_bash.bash import BashProcess


@dataclass
class LLMBashChain(Chain):
    """Chain that interprets a prompt and executes bash code to perform bash operations.

    Example:
        .. code-block:: python

            from langchain import LLMBashChain, OpenAI
            llm_bash = LLMBashChain.from_llm(OpenAI())
    """

    llm_chain: LLMChain = field(default_factory=LLMChain)
    """[Deprecated] LLM wrapper to use."""
    input_key: str = "question"  #: :meta private:
    output_key: str = "answer"  #: :meta private:
    prompt: BasePromptTemplate = field(default_factory=lambda: PROMPT)
    """[Deprecated]"""
    bash_process: BashProcess = field(default_factory=BashProcess)  #: :meta private:

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Expect output key.

        :meta private:
        """
        return [self.output_key]

    def _call(
        self,
        inputs: Dict[str, Any],
    ) -> Dict[str, str]:

        t = self.llm_chain.run(
            question=inputs[self.input_key]
        )
        t = t.strip()
        try:
            parser = self.llm_chain.prompt.output_parser
            command_list = parser.parse(t)  # type: ignore[union-attr]
            logger.debug(f"{command_list}", "Command:\n", Fore.CYAN)
        except OutputParserException as e:
            raise e
        output = self.bash_process.run(command_list)
        return {self.output_key: output}

    @property
    def _chain_type(self) -> str:
        return "llm_bash_chain"

    @classmethod
    def from_llm(
        cls,
        llm: LLMProvider,
        prompt: BasePromptTemplate = PROMPT,
        **kwargs: Any,
    ) -> LLMBashChain:
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        return cls(llm_chain=llm_chain, **kwargs)