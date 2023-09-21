#!/usr/bin/env python3
# -*-coding:utf-8-*-

import os
import ast
from dataclasses import dataclass, field
import shutil
import subprocess
from pathlib import Path
from loguru import logger
import re
from typing import List, Optional, Set

from uglygpt.base import File

VENV_NAME = ".venv"

def get_imports(file_path: str) -> List[str]:
    try:
        with open(file_path) as f:
            root = ast.parse(f.read())
    except SyntaxError:
        return []

    imports = []
    for node in ast.walk(root):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:  # relative import
                relative_module = "." * node.level + (node.module or "")
                imports.append(relative_module)
            else:  # absolute import
                imports.append(node.module)

    return imports


def get_module_path(module_name: str, file_path: str) -> Optional[str]:
    if module_name.startswith('.'):
        parts = module_name.split('.')
        module_path = Path(file_path).parent
        for part in parts:
            if part == '':
                module_path = module_path
            else:
                module_path = module_path / part
                if (module_path.with_suffix('.py')).exists():
                    return str(module_path.with_suffix('.py'))
                elif (module_path / '__init__.py').exists():
                    return str(module_path / '__init__.py')
                elif module_path.exists():
                    continue
                else:
                    return None
    else:
        module_path = Path(module_name.replace('.', '/'))
        if (module_path.with_suffix('.py')).exists():
            return str(module_path.with_suffix('.py'))
        elif (module_path / '__init__.py').exists():
            return str(module_path / '__init__.py')
        elif module_path.exists():
            return str(module_path)
        else:
            return None


def get_dependencies(file_path: str, visited: Optional[Set[str]] = None) -> List[str]:
    if visited is None:
        visited = set()

    if file_path in visited:
        return []

    visited.add(file_path)

    if not file_path.endswith('.py'):
        return []

    imports = get_imports(file_path)

    dependencies = [file_path]
    for module_name in imports:
        module_path = get_module_path(module_name, file_path)
        if module_path is not None and not Path(module_path).parent.samefile(Path(os.__file__).parent):
            dependencies.extend(get_dependencies(module_path, visited))

    return dependencies

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
    def prepare_debug(self, path:str) -> str:
        file_list = self._copy_file(path)
        for file_path in file_list:
            self._install_dependencies(file_path)
        return self.relative_path(file_list[0])

    def run_debug(self, test_name: str) -> None:
        test_path = Path(test_name)
        if test_path.is_absolute():
            try:
                test_path.relative_to(self.dir_path)
            except ValueError:
                raise ValueError(f"Test path {test_path} is not in the sandbox directory.")
        else:
            test_path = File.WORKSPACE_ROOT / test_name
        if not test_path.exists():
            raise FileNotFoundError(f"Test file {test_path} does not exist.")
        path = test_path.relative_to(self.dir_path)
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

    def _copy_file(self, file_path: str) -> List[Path]:
        file_list = get_dependencies(file_path)
        new_list: List[Path] = []
        if len(file_list) == 1:
            new_file_path = self.dir_path / Path(file_path).name
            shutil.copy(Path(file_path), new_file_path)
            new_list.append(new_file_path)
        else:
            for file_path in file_list:
                new_file_path = self.dir_path / file_path
                new_file_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(Path(file_path), new_file_path)
                new_list.append(new_file_path)
        return new_list

    def _install_dependencies(self, file_path: Path) -> None:
        with open(file_path) as file:
            content = file.read()
        dependencies = re.findall(r'^\s*(?:from|import)\s+([\w]+)(?:\.[\w]+)*', content, re.MULTILINE)
        new_dependencies = [dependency for dependency in dependencies if dependency not in self._dependencies]

        for dependency in new_dependencies:
            try:
                subprocess.run([f'{VENV_NAME}/bin/pip', 'install', dependency], cwd=self.dir_path, check=True)
                self._dependencies.append(dependency)
            except subprocess.CalledProcessError as e:
                logger.error(f'Failed to install dependency {dependency}: {e}')
                self._dependencies.append(dependency)

    @classmethod
    def relative_path(cls, path: Path) -> str:
        path = path.relative_to(File.WORKSPACE_ROOT)
        return str(path)

    @property
    def dir(self):
        return self._dir_name
