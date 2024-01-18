#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from loguru import logger
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
import subprocess

import requests
from tenacity import retry, stop_after_attempt, wait_fixed

from .utils import get_directory_structure

WORKING_DIR = Path("/home/uglyboy/Code")

@dataclass
class RepoInfo:
    description: str|None
    topics: List[str]
    language: str|None
    homepage: str|None
    updated_at: datetime
    pushes_count: int
    star_count: int
    fork_count: int
    issue_count: int

    def __str__(self):
        return f"""项目信息:
描述: {self.description}
标签: {self.topics}
编程语言: {self.language}
主页: {self.homepage}
上次更新时间: {self.updated_at}
上个月更新次数: {self.pushes_count}
标星数量: {self.star_count}
Fork 数量: {self.fork_count}
讨论 数量: {self.issue_count}
"""


@dataclass
class Repo:
    repo_name: str

    def __post_init__(self):
        if '/' not in self.repo_name or self.repo_name.count('/') != 1 or self.repo_name.startswith('/') or self.repo_name.endswith('/'):
            raise ValueError(f"Invalid repo name: {self.repo_name}")
        try:
            if not self._check_exists():
                raise ValueError(f"Repo {self.owner}/{self.name} does not exist.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to check if repo {self.owner}/{self.name} exists: {e}")
            raise

    @property
    def owner(self) -> str:
        return self.repo_name.split('/')[0]

    @property
    def name(self) -> str:
        return self.repo_name.split('/')[1]

    @property
    def path(self) -> Path:
        return WORKING_DIR / self.name

    @property
    def directory_structure(self) -> str:
        return get_directory_structure(self.path)

    def get(self, overwrite: bool = True) -> None:
        """Download or update the repo to the current working directory."""
        if not self.path.exists():
            self._clone()
            return

        if not (self.path / '.git').exists():
            if overwrite:
                self._remove_and_clone()
                return
            else:
                logger.error(f"Directory {self.path} is not a git repo.")
                raise FileExistsError(f"Directory {self.path} is not a git repo.")

        url = f"https://github.com/{self.owner}/{self.name}.git"
        try:
            remote_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], cwd=self.path).decode().strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get remote url of repo {self.owner}/{self.name}: {e}")
            raise

        if remote_url != url:
            if overwrite:
                self._remove_and_clone()
            else:
                logger.error(f"Directory {self.path} is not the correct repo.")
                raise FileExistsError(f"Directory {self.path} is not the correct repo.")
        else:
            self._pull()

    def _clone(self) -> None:
        url = f"https://github.com/{self.owner}/{self.name}.git"
        try:
            subprocess.Popen(['git', 'clone', url], cwd=WORKING_DIR).wait()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download repo {self.owner}/{self.name}: {e}")
            raise
        else:
            logger.info(f"Repo {self.owner}/{self.name} has been downloaded to {self.path}.")

    def _pull(self) -> None:
        try:
            subprocess.Popen(['git', 'pull'], cwd=self.path).wait()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to update repo {self.owner}/{self.name}: {e}")
            raise
        else:
            logger.info(f"Repo {self.owner}/{self.name} has been updated.")

    def _remove_and_clone(self) -> None:
        try:
            subprocess.Popen(['rm', '-rf', str(self.path)], cwd=WORKING_DIR).wait()
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove directory {self.path}: {e}")
            raise
        else:
            self._clone()

    @property
    def repo_info(self) -> RepoInfo|None:
        """Get the repo info from GitHub API."""
        try:
            data = self._request_github_api().json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get repo info: {e}")
            return None

        required_keys = ['description', 'topics', 'language', 'updated_at', 'stargazers_count', 'forks_count', 'open_issues_count']
        if not all(key in data for key in required_keys):
            logger.error("The response data does not contain all required fields.")
            return None

        description = data['description']
        topics = data['topics']
        language = data['language']
        homepage = data['homepage']
        updated_at = datetime.strptime(data['updated_at'], "%Y-%m-%dT%H:%M:%SZ")
        star_count = data['stargazers_count']
        fork_count = data['forks_count']
        issue_count = data['open_issues_count']

        # Calculate the number of pushes in the last month
        try:
            events = self._request_github_api("events").json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get repo events: {e}")
            return None

        one_month_ago = datetime.now() - timedelta(days=30)
        pushes = sum(1 for event in events if 'type' in event and 'created_at' in event and event['type'] == 'PushEvent' and datetime.strptime(event['created_at'], "%Y-%m-%dT%H:%M:%SZ") > one_month_ago)

        return RepoInfo(description, topics, language, homepage, updated_at, pushes, star_count, fork_count, issue_count)

    def _check_exists(self) -> bool:
        """Check if the repo exists on GitHub."""
        try:
            response = self._request_github_api()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to check if repo {self.owner}/{self.name} exists: {e}")
            raise
        else:
            if response.status_code == 200:
                logger.info(f"Repo {self.owner}/{self.name} exists.")
                return True
            else:
                logger.error(f"Repo {self.owner}/{self.name} does not exist.")
                return False

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _request_github_api(self, path: str = ""):
        url = f"https://api.github.com/repos/{self.owner}/{self.name}"
        if path:
            url += f"/{path}"
        headers = {"Accept": "application/vnd.github.mercy-preview+json"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response
