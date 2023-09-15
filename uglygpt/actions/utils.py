#!/usr/bin/env python3
# -*-coding:utf-8-*-

import re
import json
from loguru import logger
from uglygpt.chains import LLMChain


def parse_code(text: str, lang: str = "python"):
    """Parses the code from the given text.

    Args:
        text: The text containing the code.
        lang: The language of the code. Defaults to "python".

    Returns:
        The parsed code.
    """
    pattern = rf'```{lang}.*?\s+(.*)\s+```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        code = match.group(1)
    else:
        pattern = rf'```.*?\s+(.*)\s+```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            match = re.search(pattern, text+"\n```", re.DOTALL)
            if match:
                code = match.group(1)
            else:
                logger.warning(f"{pattern} not match following text:\n{text}")
                raise Exception(f"{pattern} not match following text:\n{text}")
    return code


def fix_llm_json_str(string):
    new_string = string.strip()
    try:
        json.loads(new_string)
        return new_string
    except Exception as e:
        logger.warning("fix_llm_json_str failed 1:", e)
        try:
            pattern = r'```json(.*?)```'
            match = re.findall(pattern, new_string, re.DOTALL)
            if match:
                new_string = match[-1]

            json.loads(new_string)
            return new_string
        except Exception as e:
            logger.warning("fix_llm_json_str failed 2:", e)
            try:
                new_string = new_string.replace("\n", "\\n")
                json.loads(new_string)
                return new_string
            except Exception as e:
                logger.warning("fix_llm_json_str failed 3:", e)
                llm = LLMChain(llm_name="chatgpt", prompt_template="")
                llm.llm.set_system("""Do not change the specific content, fix the json, directly return the repaired JSON, without any explanation and dialogue.
                    ```
                    """+new_string+"""
                    ```""")

                message = llm()
                logger.debug(message)
                pattern = r'```json(.*?)```'
                match = re.findall(pattern, message, re.DOTALL)
                if match:
                    return match[-1]
                return message


def parse_json(string):
    try:
        return json.loads(fix_llm_json_str(string))
    except Exception as e:
        raise json.JSONDecodeError(f"parse_json failed: {e}", string, 0)
