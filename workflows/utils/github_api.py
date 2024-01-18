#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
import base64
from datetime import datetime, timedelta
from typing import Generator
from urllib.parse import urlparse

import requests
from loguru import logger

from .file import File
from agent.config import config

@dataclass
class GithubAPI:
    token = config.github_token

    @classmethod
    def _github_api(cls, url: str, params: dict | None = None):
        url = f"https://api.github.com/{url}"
        try:
            response = requests.get(
                url, headers={'Authorization': f'token {cls.token}'}, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            raise

    @classmethod
    def fetch_readme(cls, repo_name: str) -> str | None:
        url = f"repos/{repo_name}/readme"
        try:
            response = cls._github_api(url)
        except requests.exceptions.HTTPError as err:
            logger.warning(f"Repo {repo_name} has no README.")
            return None
        if response.status_code == 200:
            content = base64.b64decode(
                response.json()['content']).decode('utf-8')
            return content
        else:
            return None

    @classmethod
    def fetch_starred_repos(cls, username: str = "uglyboy-tl") -> Generator[str, None, None]:
        url = f"users/{username}/starred"
        params = {"per_page": 100}
        while True:
            response = cls._github_api(str(url), params=params)
            items = response.json()
            link = response.headers.get('Link', '')
            if not items:
                break
            for item in items:
                yield item["full_name"]
            if 'rel="next"' not in link:
                break
            full_url = link.split(';')[0].strip('<>')
            parsed = urlparse(full_url)
            url = (parsed.path + "?" + parsed.query).lstrip('/')

    @classmethod
    def fetch_trending_file(cls) -> str:
        file_name = "docs/md/trending.md"
        if File.datetime(file_name).date() < datetime.today().date():
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            try:
                content = cls.fetch_file("uglyboy-tl/Data", f"trending/{date}.md")
            except requests.exceptions.HTTPError as err:
                logger.warning("Github Trending is not updated yet.")
                return File.load(file_name)
            except requests.exceptions.RequestException as e:
                logger.error(f"An error occurred: {e}")
                raise

            if content:
                File.save(file_name, content)
                return content
        return File.load(file_name)

    @classmethod
    def fetch_file(cls, repo_name: str, file_path: str) -> str:
        url = f"repos/{repo_name}/contents/{file_path}"
        try:
            response = cls._github_api(url)
        except requests.exceptions.HTTPError as err:
            logger.error(f"Repo {repo_name} has no {file_path}.")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            raise

        if response.status_code == 200:
            content = base64.b64decode(
                response.json()['content']).decode('utf-8')
            return content
        else:
            return ""