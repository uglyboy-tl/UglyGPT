#!/usr/bin/env python3
# -*-coding:utf-8-*-

from datetime import datetime
from loguru import logger
from pathlib import Path

def get_project_root():
    """Search upwards to find the project root directory.

    Returns:
        The path to the project root directory.

    Raises:
        Exception: If the project root directory is not found.
    """
    current_path = Path.cwd()
    while True:
        if (current_path / '.git').exists() or (current_path / '.project_root').exists() or (current_path / '.gitignore').exists():
            return current_path
        parent_path = current_path.parent
        if parent_path == current_path:
            raise Exception("Project root not found.")
        current_path = parent_path


class File:
    """Class representing a file.

    Attributes:
        WORKSPACE_ROOT: The path to the project root directory.
    """
    WORKSPACE_ROOT = get_project_root()

    @classmethod
    def save(cls, filename:str , data: str) -> None:
        """Save data to a file.

        Args:
            filename: The name of the file.
            data: The data to be saved.
        """
        file_path = cls.WORKSPACE_ROOT / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            cls._backup(file_path)
        file_path.write_text(data)
        logger.debug(f"Saving file to {file_path}")

    @classmethod
    def load(cls, filename: str):
        """Load data from a file.

        Args:
            filename: The name of the file.

        Returns:
            The data loaded from the file.
        """
        with open(cls.WORKSPACE_ROOT / filename, "r") as f:
            data = f.read()
        return data

    @classmethod
    def _backup(cls, file_path: Path):
        """Backup a file.

        Args:
            file_path: The path to the file to be backed up.
        """
        backup_path = file_path.with_name(file_path.stem + '_' + datetime.now().strftime('%Y%m%d%H%M%S') + file_path.suffix + '.bak')
        file_path.rename(backup_path)