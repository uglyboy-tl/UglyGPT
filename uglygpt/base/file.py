#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
from dataclasses import dataclass, field
from loguru import logger
from pathlib import Path

def get_project_root():
    """Search upwards to find the project root directory."""
    current_path = Path.cwd()
    while True:
        if (current_path / '.git').exists() or (current_path / '.project_root').exists() or (current_path / '.gitignore').exists():
            return current_path
        parent_path = current_path.parent
        if parent_path == current_path:
            raise Exception("Project root not found.")
        current_path = parent_path

WORKSPACE_ROOT = get_project_root()

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
