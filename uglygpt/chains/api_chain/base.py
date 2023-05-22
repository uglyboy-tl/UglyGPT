"""Chain that makes API calls and summarizes the responses to answer a question."""
from __future__ import annotations
from dataclasses import dataclass, field

from typing import Any, Dict, List, Optional

from uglygpt.base import config, logger, Fore
from uglygpt.provider import LLMProvider
from uglygpt.chains.api_chain.prompt import API_RESPONSE_PROMPT, API_URL_PROMPT
from uglygpt.chains.base import Chain
from uglygpt.chains.llm import LLMChain
from uglygpt.prompts import BasePromptTemplate
from uglygpt.utilities.requests import TextRequestsWrapper

@dataclass
class APIChain(Chain):
    """Chain that makes API calls and summarizes the responses to answer a question."""

    api_request_chain: LLMChain = field(default_factory=LLMChain)
    api_answer_chain: LLMChain = field(default_factory=LLMChain)
    requests_wrapper: TextRequestsWrapper = field(default_factory=TextRequestsWrapper)
    api_docs: str = ""
    question_key: str = "question"  #: :meta private:
    output_key: str = "output"  #: :meta private:

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.question_key]

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
        question = inputs[self.question_key]
        api_url = self.api_request_chain.run(
            question=question,
            api_docs=self.api_docs,
        )
        logger.debug(f"{api_url}","API URL:", Fore.YELLOW)
        api_response = self.requests_wrapper.get(api_url)
        if config.debug_mode:
            logger.debug(f"{api_response}","API Response:", Fore.YELLOW)
        answer = self.api_answer_chain.run(
            question=question,
            api_docs=self.api_docs,
            api_url=api_url,
            api_response=api_response,
        )
        return {self.output_key: answer}


    @classmethod
    def from_llm_and_api_docs(
        cls,
        llm: LLMProvider,
        api_docs: str,
        headers: Optional[dict] = None,
        api_url_prompt: BasePromptTemplate = API_URL_PROMPT,
        api_response_prompt: BasePromptTemplate = API_RESPONSE_PROMPT,
        **kwargs: Any,
    ) -> APIChain:
        """Load chain from just an LLM and the api docs."""
        get_request_chain = LLMChain(llm=llm, prompt=api_url_prompt)
        requests_wrapper = TextRequestsWrapper(headers=headers)
        get_answer_chain = LLMChain(llm=llm, prompt=api_response_prompt)
        return cls(
            api_request_chain=get_request_chain,
            api_answer_chain=get_answer_chain,
            requests_wrapper=requests_wrapper,
            api_docs=api_docs,
            **kwargs,
        )

    @property
    def _chain_type(self) -> str:
        return "api_chain"