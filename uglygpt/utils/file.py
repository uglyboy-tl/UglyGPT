#!/usr/bin/env python3
# -*-coding:utf-8-*-

from datetime import datetime
from loguru import logger
from pathlib import Path
from shutil import copy2
from tenacity import retry, stop_after_attempt, wait_fixed


class ProjectRootNotFoundError(Exception):
    pass


class FileNotFoundInWorkspaceError(Exception):
    pass


class File:
    WORKSPACE_ROOT: Path

    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def save(cls, filename: str | Path, data: str) -> None:
        file_path = cls.to_path(filename)
        if file_path.exists():
            cls._backup(file_path)
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(data)
        logger.debug(f"保存文件至 `{file_path}`")

    @classmethod
    def append(cls, filename: str | Path, data: str) -> None:
        file_path = cls.to_path(filename)
        if file_path.exists():
            cls._backup(file_path)
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("a", encoding="utf-8") as f:
            f.write(data)
        logger.debug(f"追加数据至 `{file_path}`")

    @classmethod
    def load(cls, filename: str | Path):
        file_path = cls.to_path(filename)
        if not file_path.exists():
            raise FileNotFoundInWorkspaceError(
                f"File {filename} not found in workspace."
            )
        return file_path.read_text()

    @classmethod
    def exists(cls, filename: str | Path) -> bool:
        file_path = cls.to_path(filename)
        return file_path.exists()

    @classmethod
    def datetime(cls, filename: str | Path) -> datetime:
        file_path = cls.to_path(filename)
        if not file_path.exists():
            return datetime.fromtimestamp(0)
        return datetime.fromtimestamp(file_path.stat().st_mtime)

    @staticmethod
    def get_project_root(filename: str | Path) -> Path:
        if isinstance(filename, str):
            current_path = Path(filename).resolve()
        else:
            current_path = filename.resolve()
        while True:
            if (
                (current_path / ".git").exists()
                or (current_path / ".project_root").exists()
                or (current_path / ".gitignore").exists()
            ):
                return current_path
            parent_path = current_path.parent
            if parent_path == current_path:
                raise ProjectRootNotFoundError("Project root not found.")
            current_path = parent_path

    @classmethod
    def path_to_filename(cls, filename: str | Path) -> str:
        p = cls.to_path(filename)
        relative_p = p.relative_to(File.WORKSPACE_ROOT)
        parts = relative_p.parts
        new_parts = []
        for part in parts:
            if part == parts[-1] and "." in part:
                part = Path(part).stem
            temp = part.replace("_", "__")
            new_parts.append(temp)
        return "_".join(new_parts)

    @classmethod
    def to_path(cls, filename: str | Path) -> Path:
        if isinstance(filename, str):
            file_path = Path(filename)
        else:
            file_path = filename
        return file_path if file_path.is_absolute() else cls.WORKSPACE_ROOT / filename

    @classmethod
    def _backup(cls, file_path: Path):
        backup_path = file_path.with_suffix(
            file_path.suffix + "." + datetime.now().strftime("%Y%m%d%H%M%S") + ".bak"
        )
        copy2(file_path, backup_path)


File.WORKSPACE_ROOT = File.get_project_root(__file__)
