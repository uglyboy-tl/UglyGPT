#!/usr/bin/env python3
#-*-coding:utf-8-*-

import os
from dataclasses import dataclass
from loguru import logger

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@dataclass
class File:
    @classmethod
    def save(cls, filename, data):
        file_path = WORKSPACE_ROOT / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(data)
        logger.debug(f"Saving file to {file_path}")

    @classmethod
    def load(cls, filename):
        with open(WORKSPACE_ROOT / filename, "r") as f:
            data = f.read()
        return data