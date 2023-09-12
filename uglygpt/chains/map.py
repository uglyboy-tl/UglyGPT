from dataclasses import dataclass, field
from typing import Dict, List
from loguru import logger
#from pathos.multiprocessing import ProcessingPool as Pool
from multiprocessing import Pool

from uglygpt.llm import LLMProvider, get_llm_provider
from .base import Chain
from .llm import LLMChain


@dataclass
class MapChain(Chain):
    input_key: str = "input_documents"  #: :meta private:
    map_chain: Chain = field(default_factory=LLMChain)  #: :meta private:
    rank_key: str = "rank"  #: :meta private:

    @property
    def input_keys(self) -> List[str]:
        return [self.input_key]

    def _call(self,inputs: Dict[str, List[str]],) -> Dict[str, str]:
        documents = inputs[self.input_key]
        text_dicts = [{"rank": i, "text": text} for i, text in enumerate(documents)]
        # 并行处理，保留原有顺序的序号

        pool = Pool()

        def map_func(text_dict):
            # Other keys are assumed to be needed for LLM prediction
            other_keys: Dict = {k: v for k,
                                v in inputs.items() if k != self.input_key}
            other_keys[self.map_chain.input_keys[0]] = text_dict["text"]
            result = self.map_chain(other_keys)
            result.update({"rank": text_dict["rank"]})
            logger.debug("Mapping Result:", result)
            return result

        results = pool.map(map_func, text_dicts)
        pool.close()
        # 重新依据 self.rank_key 的值进行排序，默认是原有顺序。
        results = sorted(results, key=lambda x: x[self.rank_key])
        # 合并结果
        results_text = "\n".join(
            [result[self.map_chain.output_keys[0]] for result in results])


        logger.debug("Mapping Results:", results_text)
