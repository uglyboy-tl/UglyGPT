#!/usr/bin/env python3

from dataclasses import dataclass, field
import re

from uglychain import Model
from uglychain.storage import SQLiteStorage
from .utils import parse_markdown
from uglygpt.utilities import GithubAPI, FeishuAPI

@dataclass
class FeishuTrending():
    filename: str = "data/github/github.db"
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
            card = {
                "config": {
                    "wide_screen_mode": True
                },
                "elements": [
                    {
                        "tag": "note",
                        "elements": [
                            {
                            "tag": "plain_text",
                            "content": f"{self._repo_descriptions[name]}"
                            }
                        ]
                    },
                    {
                    "tag": "markdown",
                    "content": f"{self._data[name]}"
                    },
                    {
                    "tag": "action",
                    "actions": [
                        {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "前往项目"
                        },
                        "type": "primary",
                        "multi_url": {
                            "url": f"https://www.github.com/{name}",
                            "pc_url": "",
                            "android_url": "",
                            "ios_url": ""
                        }
                        }
                    ]
                    }
                ],
                "header": {
                    "template": "blue",
                    "title": {
                    "content": f"{name}",
                    "tag": "plain_text"
                    }
                }
            }
            FeishuAPI.post(card)
