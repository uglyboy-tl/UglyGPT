#!/usr/bin/env python3
# -*-coding:utf-8-*-

import re
import json
from typing import Dict

from loguru import logger

from uglygpt import LLM


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
            logger.warning(
                f"parse_code: {lang} not match following text:\n{text}")
        else:
            match = re.search(pattern, text+"\n```", re.DOTALL)
            if match:
                code = match.group(1)
                logger.warning(
                    "code in code block not end with ```, we add it automatically.")
            else:
                logger.warning(f"{pattern} not match following text:\n{text}")
                raise Exception(f"{pattern} not match following text:\n{text}")
    return code


def fix_llm_json_str(string: str):
    """Fixes the JSON string.

    Args:
        string: The JSON string to fix.

    Returns:
        The fixed JSON string.
    """
    new_string = re.sub(r',\s*}', '}', string)
    new_string = re.sub(r',\s*]', ']', new_string)
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
                llm = LLM()
                message = llm(
                    """Do not change the specific content, fix the json, directly return the repaired JSON, without any explanation and dialogue.\n```\n"""+new_string+"""\n```""")
                logger.debug(message)
                pattern = r'```json(.*?)```'
                match = re.findall(pattern, message, re.DOTALL)
                if match:
                    return match[-1]
                return message


def parse_json(string):
    """Parses the JSON string.

    Args:
        string: The JSON string to parse.

    Returns:
        The parsed JSON object.
    Raises:
        json.JSONDecodeError: If the JSON string cannot be decoded.
    """
    try:
        return json.loads(fix_llm_json_str(string))
    except Exception as e:
        raise json.JSONDecodeError(f"parse_json failed: {e}", string, 0)


def parse_markdown(markdown_text: str) -> Dict[str, str]:
    """
    Convert markdown text to dictionary.

    Parameters:
    markdown_text (str): The markdown text.

    Returns:
    dict: The dictionary with title as key and text as value.
    """
    if not isinstance(markdown_text, str):
        raise ValueError('The input markdown_text must be a string.')
    pattern = r'(?m)^## (.*?)\n(.*?)(?=^## |\Z)'
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    return {title: text.strip() for title, text in matches}
