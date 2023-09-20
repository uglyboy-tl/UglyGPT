#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
import shutil
import subprocess
from pathlib import Path
from loguru import logger
import re

from uglygpt.base import File

VENV_NAME = ".venv"

class TestFailedError(Exception):
    pass

@dataclass
class Sandbox:
    _dir_name: str = "sandbox"
    _dependencies: list = field(default_factory=list)

    def __post_init__(self):
        self.dir_path = File.WORKSPACE_ROOT / self._dir_name

    def init(self) -> None:
        # If the sandbox directory exists, delete all files and subdirectories
        shutil.rmtree(self.dir_path, ignore_errors=True)

        # Create the sandbox directory
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def setup_venv(self) -> None:
        # Create a virtual environment in the sandbox directory
        try:
            subprocess.run(['python3', '-m', 'venv', VENV_NAME], cwd=self.dir_path, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to create virtual environment: {e}')

    # TODO: 未来需要添加目标文件依赖的其他文件的拷贝，以及其他文件的依赖包的安装
    def prepare_test(self, path:str) -> str:
        file_path = self._copy_file(path)
        self._install_dependencies(file_path)
        return self.relative_path(file_path)

    def run_test(self, test_path: str) -> None:
        path = File.WORKSPACE_ROOT / test_path
        path = path.relative_to(self.dir_path)
        try:
            process = subprocess.Popen(f"{self.test_command} {path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.dir_path)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                logger.warning(f"Test failed. Stderr: {stderr}")
                raise TestFailedError(f"{stderr}")

            logger.info(f"Test passed successfully. Stdout: {stdout}")
        except Exception as e:
            raise

    @property
    def test_command(self) -> str:
        python_path = self.dir_path/ VENV_NAME / "bin"/ "python"
        return f"{python_path} -m unittest"

    def _copy_file(self, file_path: str) -> Path:
        # Create a new Path object for the new file path
        new_file_path = self.dir_path / Path(file_path).name

        # Copy the file to the sandbox directory
        shutil.copy(file_path, new_file_path)

        return new_file_path

    def _install_dependencies(self, file_path: Path) -> None:
        with open(file_path) as file:
            content = file.read()
        dependencies = re.findall(r'^\s*(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
        new_dependencies = [dependency for dependency in dependencies if dependency not in self._dependencies]

        for dependency in new_dependencies:
            try:
                subprocess.run([f'{VENV_NAME}/bin/pip', 'install', dependency], cwd=self.dir_path, check=True)
                self._dependencies.append(dependency)
            except subprocess.CalledProcessError as e:
                logger.error(f'Failed to install dependency {dependency}: {e}')

    @classmethod
    def relative_path(cls, path: Path) -> str:
        path = path.relative_to(File.WORKSPACE_ROOT)
        return str(path)

    @property
    def dir(self):
        return self._dir_name
