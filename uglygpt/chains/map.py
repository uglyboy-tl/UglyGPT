#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from typing import Any, Dict, List
from pathos.multiprocessing import ProcessingPool as Pool
import json

from .base import Chain
from .llm import LLMChain


@dataclass
class MapChain(Chain):
    chain: Chain = field(default_factory=LLMChain)
    map_keys: List[str] = field(default_factory=lambda: ["input"])

    @property
    def input_keys(self) -> List[str]:
        return self.chain.input_keys

    def _validate_inputs(self, inputs: Dict[str, Any]) -> None:
        self.num = len(inputs[self.map_keys[0]])
        for map_key in self.map_keys:
            assert map_key in self.input_keys, f"MapChain expects {map_key} to be in input_keys"
            assert isinstance(inputs[map_key], List), f"MapChain expects {map_key} to be a list of strings"
            assert len(inputs[map_key]) == self.num, f"MapChain expects {map_key} to be a list of strings with the same length"
        super()._validate_inputs(inputs)

    def _call(self, inputs: Dict[str, Any]) -> str:
        inputs_list = []
        for i in range(self.num):
            input = {}
            for map_key in self.map_keys:
                input[map_key] = inputs[map_key][i]
            input["index"] = i
            inputs_list.append(input)

        pool = Pool()
        def map_func(input):
            new_input: Dict = {k: v for k, v in inputs.items() if k not in self.map_keys}
            for mapping_key in self.map_keys:
                new_input[mapping_key] = input[mapping_key]
            result = self.chain(**new_input)
            return {"index":input["index"], "result":result}
        results = pool.map(map_func, inputs_list)
        pool.close()

        # 重新依据 self.rank_key 的值进行排序，默认是原有顺序。
        results = sorted(results, key=lambda x: x["index"])
        results = [result["result"] for result in results]

        results_text = json.dumps(results, indent=4, ensure_ascii=False)
        return results_text
