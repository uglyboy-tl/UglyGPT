import re
import ast
from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple

from uAgent.base import logger
from uAgent.chains.output_parsers.base import BaseOutputParser

@dataclass
class MappingOutputParser(BaseOutputParser):
    format_example: str = ""
    output_mapping: Dict[str, Any] = field(default_factory=dict)

    @property
    def _type(self) -> str:
        return "mapping"

    @property
    def output_variables(self) -> List[str]:
        return self.output_mapping.keys()

    def get_format_instructions(self) -> str:
        return self.format_example

    def parse(self, text: str) -> Dict[str, Any]:
        block_dict = parse_blocks(text)
        parsed_data = {}
        for block, content in block_dict.items():
            try:
                content = parse_code(text=content)
            except Exception:
                pass
            typing_define = self.output_mapping.get(block, None)
            if isinstance(typing_define, tuple):
                typing = typing_define[0]
            else:
                typing = typing_define
            if typing == List[str] or typing == List[Tuple[str, str]]:
                # 尝试解析list
                try:
                    content = parse_file_list(text=content)
                except Exception:
                    pass
            # TODO: 多余的引号去除有风险，后期再解决
            # elif typing == str:
            #     # 尝试去除多余的引号
            #     try:
            #         content = cls.parse_str(text=content)
            #     except Exception:
            #         pass
            parsed_data[block] = content
        return parsed_data

def parse_blocks(text: str):
    # 首先根据"##"将文本分割成不同的block
    blocks = text.split("##")

    # 创建一个字典，用于存储每个block的标题和内容
    block_dict = {}

    # 遍历所有的block
    for block in blocks:
        # 如果block不为空，则继续处理
        if block.strip() != "":
            # 将block的标题和内容分开，并分别去掉前后的空白字符
            block_title, block_content = block.split("\n", 1)
            # LLM可能出错，在这里做一下修正
            if block_title[-1] == ":":
                block_title = block_title[:-1]
            block_dict[block_title.strip()] = block_content.strip()

    return block_dict

def parse_file_list(text: str) -> list[str]:
    # Regular expression pattern to find the tasks list.
    pattern = r'\s*(.*=.*)?(\[.*\])'

    # Extract tasks list string using regex.
    match = re.search(pattern, text, re.DOTALL)
    if match:
        tasks_list_str = match.group(2)

        # Convert string representation of list to a Python list using ast.literal_eval.
        tasks = ast.literal_eval(tasks_list_str)
    else:
        tasks = text.split("\n")
    return tasks

def parse_code(text: str, lang: str = "") -> str:
    pattern = rf'```{lang}.*?\s+(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        code = match.group(1)
    else:
        raise Exception
    return code