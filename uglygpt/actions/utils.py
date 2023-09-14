#!/usr/bin/env python3
# -*-coding:utf-8-*-

from typing import List, Tuple, Dict, Any
import re
import ast
import json
from loguru import logger
from uglygpt.chains import LLMChain


def code_parse(text: str, lang: str = "python"):
    pattern = rf'```{lang}.*?\s+(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        code = match.group(1)
    else:
        logger.warning(f"{pattern} not match following text:")
        logger.warning(text)
        raise Exception
    return code


def file_list_parse(text: str) -> list[str]:
    # Regular expression pattern to find the tasks list.
    try:
        text = code_parse(text)
    except Exception:
        pass

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


def blocks_parse(text: str):
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


def mapping_parse(text: str, output_mapping: Dict[str, Any]) -> Dict[str, Any]:
    block_dict = blocks_parse(text)
    parsed_data = {}
    for block, content in block_dict.items():
        try:
            content = code_parse(text=content)
        except Exception:
            pass
        typing_define = output_mapping.get(block, None)
        if isinstance(typing_define, tuple):
            typing = typing_define[0]
        else:
            typing = typing_define
        if typing == List[str] or typing == List[Tuple[str, str]]:
            # 尝试解析list
            try:
                content = file_list_parse(text=content)
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


def fix_llm_json_str(string):
    new_string = string.strip()
    try:
        json.loads(new_string)
        return new_string
    except Exception as e:
        print("fix_llm_json_str failed 1:", e)
        try:
            pattern = r'```json(.*?)```'
            match = re.findall(pattern, new_string, re.DOTALL)
            if match:
                new_string = match[-1]

            json.loads(new_string)
            return new_string
        except Exception as e:
            print("fix_llm_json_str failed 2:", e)
            try:
                new_string = new_string.replace("\n", "\\n")
                json.loads(new_string)
                return new_string
            except Exception as e:
                print("fix_llm_json_str failed 3:", e)
                llm = LLMChain(llm_name="chatgpt")
                llm.llm.set_system("""Do not change the specific content, fix the json, directly return the repaired JSON, without any explanation and dialogue.
                    ```
                    """+new_string+"""
                    ```""")

                message = llm()
                pattern = r'```json(.*?)```'
                match = re.findall(pattern, message, re.DOTALL)
                if match:
                    return match[-1]

                return message


def parse_json(string):
    return json.loads(fix_llm_json_str(string))
