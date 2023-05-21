"""Chain that interprets a prompt and executes python code to do math."""
from __future__ import annotations
from dataclasses import dataclass, field

import math
import re
from typing import Any, Dict, List

import numexpr

from uglygpt.base import logger, Fore
from uglygpt.provider.llm import LLMProvider

from uglygpt.chains.base import Chain
from uglygpt.chains.llm import LLMChain
from uglygpt.chains.llm_math.prompt import PROMPT
from uglygpt.prompts.base import BasePromptTemplate

@dataclass
class LLMMathChain(Chain):
    """Chain that interprets a prompt and executes python code to do math.

    Example:
        .. code-block:: python

            from langchain import LLMMathChain, OpenAI
            llm_math = LLMMathChain.from_llm(OpenAI())
    """

    llm_chain: LLMChain = field(default_factory=LLMChain)
    """[Deprecated] LLM wrapper to use."""
    prompt: BasePromptTemplate = field(default_factory=lambda: PROMPT)
    """[Deprecated] Prompt to use to translate to python if necessary."""
    input_key: str = "question"  #: :meta private:
    output_key: str = "answer"  #: :meta private:

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

    def _evaluate_expression(self, expression: str) -> str:
        try:
            local_dict = {"pi": math.pi, "e": math.e}
            output = str(
                numexpr.evaluate(
                    expression.strip(),
                    global_dict={},  # restrict access to globals
                    local_dict=local_dict,  # add common mathematical functions
                )
            )
        except Exception as e:
            raise ValueError(
                f'LLMMathChain._evaluate("{expression}") raised error: {e}.'
                " Please try again with a valid numerical expression"
            )

        # Remove any leading and trailing brackets from the output
        return re.sub(r"^\[|\]$", "", output)

    def _process_llm_result(
        self, llm_output: str
    ) -> Dict[str, str]:
        llm_output = llm_output.strip()
        text_match = re.search(r"^```text(.*?)```", llm_output, re.DOTALL)
        if text_match:
            expression = text_match.group(1)
            logger.debug(expression, "Expression:\n", Fore.CYAN)
            output = self._evaluate_expression(expression)
            answer = output
        elif "Answer:" in llm_output:
            logger.warn("LLM returned answer without `numexpr`, assuming it is correct.")
            answer = llm_output.split("Answer:")[-1]
        else:
            logger.error(f"LLM returned unknown format: {llm_output}")
            raise ValueError(f"unknown format from LLM: {llm_output}")
        return {self.output_key: answer}

    def _call(
        self,
        inputs: Dict[str, str],
    ) -> Dict[str, str]:
        llm_output = self.llm_chain.run(
            question=inputs[self.input_key],
            stop=["```output"],
        )
        return self._process_llm_result(llm_output)


    @property
    def _chain_type(self) -> str:
        return "llm_math_chain"

    @classmethod
    def from_llm(
        cls,
        llm: LLMProvider,
        prompt: BasePromptTemplate = PROMPT,
        **kwargs: Any,
    ) -> LLMMathChain:
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        return cls(llm_chain=llm_chain, **kwargs)