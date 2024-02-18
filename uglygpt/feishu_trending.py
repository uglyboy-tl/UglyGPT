#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from datetime import datetime
import re
import hashlib
import base64
import hmac
import json

import requests
from loguru import logger

from uglychain import Model
from uglychain.storage import SQLiteStorage
from .utils import parse_markdown, config
from uglygpt.worker.github import GithubAPI

@dataclass
class FeishuTrending():
    filename: str = "data/github/github.db"
    bot_webhook: str = config.feishu_webhook
    secret: str = config.feishu_secret
    summarizer_db: SQLiteStorage = field(init=False)
    category_db: SQLiteStorage = field(init=False)
    model: Model = Model.DEFAULT

    def __post_init__(self):
        self.summarizer_db = SQLiteStorage(self.filename, "ReadmeSummarizer")
        self.category_db = SQLiteStorage(self.filename, "Category")
        self.old = SQLiteStorage(self.filename, "Feishu", 30)
        self.config = SQLiteStorage(self.filename, "Config")

        self._repo_names = []
        self._repo_descriptions = {}

        text = GithubAPI.fetch_trending_file()
        for language in ["All Languages", "Python", "Typescript", "Rust", "Go", "Html", "Css"]:
            self._fetch_trending_repos(text, language)

        # 去重
        _set = set(self._repo_names)
        self._repo_names = list(_set)

        old_repos = self.old.load(self._repo_names, "timestamp != date(\'now\',\'localtime\')")
        self._repo_names = [i for i in self._repo_names if i not in old_repos.keys()]

        # 加载数据库
        self._data = self.summarizer_db.load(self._repo_names)
        _category = self.category_db.load(self._repo_names)

        self._repo_names = [i for i in self._repo_names if _category.get(i) == "AI"]
        self.old.save({i:"1" for i in self._repo_names})

    def _fetch_trending_repos(self, text: str, language: str = "All Languages"):
        markdown = parse_markdown(text)
        pattern = r'\-\s\[(.*?)\]\((.*?)\)\s-\s(.*?)\n'
        matches = re.findall(pattern, markdown[language])

        for match in matches:
            name, _, context = match
            self._repo_names.append(name)
            self._repo_descriptions[name] = context

    def feishu_output(self):
        for name in self._repo_names:
            _lines = []
            _line = []
            url = f"https://www.github.com/{name}"
            part = {
					"tag": "a",
					"href": url,
					"text": name,
				}
            _line.append(part)
            part = {
                    "tag": "text",
                    "text": f" - {self._repo_descriptions[name]}"
            }

            _line.append(part)
            _lines.append(_line)
            _lines.append([])
            for line in self._data[name].split("\n"):
                _line = []
                part = {
                    "tag": "text",
                    "text": line
                }
                _line.append(part)
                _lines.append(_line)
            data = {"post":{"zh_cn":{"title":name,"content":_lines}}}
            self.post(data)

    def post(self, message: str|dict):
        timestamp = int(datetime.now().timestamp())
        if isinstance(message, dict):
            data = {
                "timestamp": timestamp,
                "sign": self.gen_sign(timestamp),
                "msg_type": "post",
                "content": message
            }
        else:
            data = {
                "timestamp": timestamp,
                "sign": self.gen_sign(timestamp),
                "msg_type": "text",
                "content": {
                    "text": message
                }
            }
        try:
            response = requests.post(
                self.bot_webhook, headers={"Content-Type": "application/json"}, data=json.dumps(data))
            #response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            raise
        result = response.json()

        if result.get("code") != 0:
            logger.debug(result)
            logger.error(f"An error occurred: {result['msg']}")
            raise Exception(result['msg'])

    def gen_sign(self, timestamp):
        # 拼接timestamp和secret
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign