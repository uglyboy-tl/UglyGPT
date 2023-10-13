#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
import base64
from datetime import datetime
from typing import Generator

import requests
from loguru import logger

from uglygpt.base import File, config


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
        response = cls._github_api(url)
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
            url = link.split(';')[0].strip('<>')

    @classmethod
    def fetch_trending_file(cls) -> str:
        file_name = "docs/md/trending.md"
        if File.datetime(file_name).date() < datetime.today().date():
            date = datetime.now().strftime("%Y-%m-%d")
            url = f"repos/uglyboy-tl/uglyboy-tl/contents/trending/{date}.md"
            try:
                response = cls._github_api(url)
            except requests.exceptions.HTTPError as err:
                logger.warning("Github Trending is not updated yet.")
                return File.load(file_name)
            except requests.exceptions.RequestException as e:
                logger.error(f"An error occurred: {e}")
                raise

            if response.status_code == 200:
                content = base64.b64decode(
                    response.json()['content']).decode('utf-8')
                File.save(file_name, content)
                return content
            else:
                raise Exception("Github Trending is not updated yet.")
        return File.load(file_name)
