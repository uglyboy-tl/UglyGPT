#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from datetime import datetime
import urllib.parse
import re

from loguru import logger

from uglygpt.base import File
from uglygpt.chains import parse_markdown
from uglygpt.utils.github_api import GithubAPI
from uglygpt.utils.sqlite import KVCache
from uglygpt.actions.infermation.summarizer import ReadmeSummarizer
from uglygpt.actions.infermation.category import Category


@dataclass
class GithubTrending():
    output: str = "/home/uglyboy/Documents/Obsidian/📥 收件箱/Github 趋势.md"
    filename: str = "resource/github.db"
    summarizer: ReadmeSummarizer = field(init=False)
    category: Category = field(init=False)

    def __post_init__(self):
        self.summarizer = ReadmeSummarizer(self.filename)
        self.category = Category(self.filename)
        self.finished = KVCache(self.filename, "Finished")
        self.config = KVCache(self.filename, "Config")

        self._repo_names = []
        self._repo_descriptions = {}

        date = self.config.get("Date").get("Date","")
        if date != datetime.now().strftime("%Y-%m-%d"):
            self._check_finished()

        text = GithubAPI.fetch_trending_file()
        for language in ["All Languages", "Python", "Typescript"]:
            self._fetch_trending_repos(text, language)
        self._remove_finished_repos()
        self._data = self.summarizer._load(self._repo_names)

    def _check_finished(self):
        logger.info("Updating The Finished Repos...")
        self._set_finished_with_favourite()
        self._set_finished_with_stars()
        self._set_finished_with_markdown()
        self.config.set({"Date": datetime.now().strftime("%Y-%m-%d")})

    def _remove_finished_repos(self):
        finished_repos = self.finished.get(self._repo_names)
        self._repo_names = [name for name in self._repo_names if name not in finished_repos.keys()]

    def _set_finished_with_stars(self):
        stars = set(GithubAPI.fetch_starred_repos())
        data = {k: "Starred" for k in stars}
        self.finished.set(data)

    def _set_finished_with_markdown(self):
        markdown_text = File.load(self.output)
        pattern = r"- \[x\] \[(?P<name>.+?)\]"
        matches = re.findall(pattern, markdown_text, re.MULTILINE)
        old = self.finished.get(matches)
        data = {k: "Marked" for k in matches if k not in old.keys()}
        self.finished.set(data)

    def _set_finished_with_favourite(self):
        dir_path = File.to_path(self.output).parent
        favourite_List = []
        file_index = {}
        for file in dir_path.iterdir():
            if file.is_file():
                file_name = file.name
                if file_name.count('%2F') == 1:
                    name = urllib.parse.unquote(file_name)[:-3]
                    favourite_List.append(name)
                    if file.stat().st_size == 0:
                        file_index[name] = file
        dict = self.summarizer._load(favourite_List)
        data = {}
        for name in favourite_List:
            if name not in dict.keys():
                continue
            data[name] = "Liked"
            if name in file_index.keys():
                context = "## " + name + "\n\n"
                for line in dict[name].split("\n"):
                    context += f"> {line}\n"
                context += "\n"
                File.save(file_index[name], context)
        self.finished.set(data)

    def _fetch_trending_repos(self, text: str, language: str = "All Languages"):
        markdown = parse_markdown(text)
        pattern = r'\-\s\[(.*?)\]\((.*?)\)\s-\s(.*?)\n'
        matches = re.findall(pattern, markdown[language])

        for match in matches:
            name, _, context = match
            self._repo_names.append(name)
            self._repo_descriptions[name] = context

    def _fetch_summarizer(self):
        readme_list = []
        description_list = []

        new_repo_names = [
            repo_name for repo_name in self._repo_names if repo_name not in self._data.keys()]

        for repo_name in new_repo_names:
            readme = GithubAPI.fetch_readme(repo_name)
            if readme:
                if len(readme) > 40000:
                    readme = readme[:40000]
                readme_list.append(readme)
                description_list.append(self._repo_descriptions[repo_name])

        datas = self.summarizer.run(
            new_repo_names, readme_list, description_list)

        self._data.update(datas)

    def _fetch_category(self):
        category_list = self.category.run(self._repo_names, self._data)
        return category_list

    def output_markdown(self, filename: str | None = None):
        if filename:
            self.output = filename
        # 先更新数据库
        self._fetch_summarizer()
        # 更新分类，并获得分类结果
        category_list = self._fetch_category()

        # 生成 markdown
        markdown_txt = ""
        for category in ["AI", "后端", "前端", "资料", "其他"]:
            markdown_txt += f"## {category}\n\n"
            for repo_name in category_list[category]:
                if repo_name not in self._data.keys():
                    continue
                name = urllib.parse.quote(repo_name, safe='')
                url = f"https://www.github.com/{repo_name}"
                markdown_txt += f"- [ ] [{repo_name}]({name}) - {self._repo_descriptions[repo_name]} [![](https://img.shields.io/badge/Github-black)]({url}) \n\n"
                for line in self._data[repo_name].split("\n"):
                    markdown_txt += f"> {line}\n"
                markdown_txt += "\n"

        File.save(self.output, markdown_txt)