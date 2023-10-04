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
    def save(cls, filename: str|Path, data: str) -> None:
        file_path = cls._get_filepath(filename)
        if file_path.exists():
            cls._backup(file_path)
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(data)
        logger.debug(f"保存文件至 `{file_path}`")

    @classmethod
    def load(cls, filename: str|Path):
        file_path = cls._get_filepath(filename)
        if not file_path.exists():
            raise FileNotFoundInWorkspaceError(f"File {filename} not found in workspace.")
        return file_path.read_text()

    @classmethod
    def exists(cls, filename: str|Path) -> bool:
        file_path = cls._get_filepath(filename)
        return file_path.exists()

    @staticmethod
    def get_project_root(filename: str|Path) -> Path:
        if isinstance(filename, str):
            current_path = Path(filename).resolve()
        else:
            current_path = filename.resolve()
        while True:
            if (current_path / '.git').exists() or (current_path / '.project_root').exists() or (current_path / '.gitignore').exists():
                return current_path
            parent_path = current_path.parent
            if parent_path == current_path:
                raise ProjectRootNotFoundError("Project root not found.")
            current_path = parent_path

    @classmethod
    def path_to_filename(cls, filename: str|Path) -> str:
        # 创建一个 Path 对象
        p = cls._get_filepath(filename)
        # 获取相对于 workspace_root 的路径
        relative_p = p.relative_to(File.WORKSPACE_ROOT)
        # 将路径分割成各个部分
        parts = relative_p.parts
        # 对每个部分处理
        new_parts = []
        for part in parts:
            # 如果是最后一部分（即文件名），并且包含一个点，则去掉后缀
            if part == parts[-1] and '.' in part:
                part = Path(part).stem
            # 将所有的单下划线替换成双下划线
            temp = part.replace('_', '__')
            # 添加到新的部分列表中
            new_parts.append(temp)
        # 将所有的部分用单下划线连接，然后添加后缀 '.log'
        return '_'.join(new_parts)

    @classmethod
    def _get_filepath(cls, filename: str|Path) -> Path:
        if isinstance(filename, str):
            file_path = Path(filename)
        else:
            file_path = filename
        return file_path if file_path.is_absolute() else cls.WORKSPACE_ROOT / filename

    @classmethod
    def _backup(cls, file_path: Path):
        backup_path = file_path.with_suffix(file_path.suffix + '.' + datetime.now().strftime('%Y%m%d%H%M%S') + '.bak')
        copy2(file_path, backup_path)

File.WORKSPACE_ROOT = File.get_project_root(__file__)