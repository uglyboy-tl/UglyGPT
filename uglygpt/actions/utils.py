#!/usr/bin/env python3
#-*-coding:utf-8-*-

from dataclasses import dataclass
import re
import ast
import subprocess

from uglygpt.base import logger

def code_parse(text: str, lang: str = "python"):
    pattern = rf'```{lang}.*?\s+(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        code = match.group(1)
    else:
        logger.error(f"{pattern} not match following text:")
        logger.error(text)
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

def code_running(code: str, lang: str = "python") -> str:
    if lang == "python":
        locals = {}
        exec(code, globals(), locals)
        return locals['result']
    elif lang == "bash":
        process = subprocess.Popen(code, stdout=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        if error:
            logger.error(f'Error: {error}')
        return output.decode('utf-8')