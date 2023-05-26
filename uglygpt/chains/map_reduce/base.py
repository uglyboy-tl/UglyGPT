from __future__ import annotations
from dataclasses import dataclass, field
from pathos.multiprocessing import ProcessingPool as Pool
from typing import Dict, List

from uglygpt.base import config, logger, Fore
from uglygpt.chains.base import Chain
from uglygpt.chains.llm import LLMChain

@dataclass
class AnalyzeDocumentChain(Chain):
    """Chain that splits documents, then analyzes it in pieces."""
    input_key: str = "input_documents"  #: :meta private:
    map_chain: Chain = field(default_factory=LLMChain)  #: :meta private:
    reduce_chain: Chain = None  #: :meta private:
    rank_key: str = "rank"  #: :meta private:

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Return output key.

        :meta private:
        """
        if self.reduce_chain is None:
            return ["output"]
        return self.reduce_chain.output_keys

    def _call(
        self,
        inputs: Dict[str, List[str]],
    ) -> Dict[str, str]:
        documents = inputs[self.input_key]
        text_dicts = [{"rank":i ,"text": text} for i,text in enumerate(documents)]
        # 并行处理，保留原有顺序的序号

        pool = Pool()

        def map_func(text_dict):
            # Other keys are assumed to be needed for LLM prediction
            other_keys: Dict = {k: v for k, v in inputs.items() if k != self.input_key}
            other_keys[self.map_chain.input_keys[0]] = text_dict["text"]
            result = self.map_chain(other_keys)
            result.update({"rank":text_dict["rank"]})
            if config.debug_mode:
                logger.debug(str(result), "Mapping Result:", Fore.GREEN)
            return result

        results = pool.map(map_func, text_dicts)
        pool.close()
        # 重新依据 self.rank_key 的值进行排序，默认是原有顺序。
        results = sorted(results, key=lambda x: x[self.rank_key])
        # 合并结果
        results_text = "\n".join([result[self.map_chain.output_keys[0]] for result in results])

        if config.debug_mode:
            logger.debug(results_text, "Mapping Results:", Fore.GREEN)

        # 重新组合
        if self.reduce_chain is not None:
            other_keys: Dict = {k: v for k, v in inputs.items() if k != self.input_key}
            other_keys[self.reduce_chain.input_keys[0]] = results_text
            return self.reduce_chain(other_keys)
        else:
            return {self.output_keys[0]: results_text}