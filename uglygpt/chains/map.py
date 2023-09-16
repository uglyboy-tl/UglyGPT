from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from loguru import logger
from pathos.multiprocessing import ProcessingPool as Pool

from .base import Chain
from .llm import LLMChain


@dataclass
class MapChain(Chain):
    map_chain: Chain = field(default_factory=LLMChain)
    reduce_chain: Optional[Chain|None] = None
    mapping_key: str = "input"

    @property
    def input_keys(self) -> List[str]:
        return self.map_chain.input_keys

    def _validate_inputs(self, inputs: Dict[str, Any]) -> None:
        if self.mapping_key not in self.input_keys:
            raise ValueError(
                f"MapChain expects {self.mapping_key} to be in input_keys")
        super()._validate_inputs(inputs)
        if not isinstance(inputs[self.mapping_key], List):
            raise ValueError(
                f"MapChain expects {self.mapping_key} to be a list of strings")

    def _call(self, inputs: Dict[str, Any]) -> str:
        text_dicts = [{"index": i, "text": str(item)} for i, item in enumerate(inputs[self.mapping_key])]

        pool = Pool()
        def map_func(text_dict):
            new_input: Dict = {k: v for k, v in inputs.items() if k != self.mapping_key}
            new_input[self.mapping_key] = text_dict["text"]
            result = self.map_chain(**new_input)
            return {"index":text_dict["index"], "result":result}
        results = pool.map(map_func, text_dicts)
        pool.close()

        # 重新依据 self.rank_key 的值进行排序，默认是原有顺序。
        results = sorted(results, key=lambda x: x["index"])
        results = [result["result"] for result in results]

        # 合并结果
        if not self.reduce_chain:
            results_text = "\n".join(results)

            return results_text
        else:
            # TODO: 未完成
            return self.reduce_chain(results)
