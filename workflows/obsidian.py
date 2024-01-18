#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from datetime import datetime
import urllib.parse
import re
from time import sleep

from loguru import logger

from .utils import GithubAPI, KVCache, File, parse_markdown
from .actions.obsidian.summarizer import ReadmeSummarizer
from .actions.obsidian.category import Category

FRONT_MATTER = """---
date: {time}
lastmod: {time}
url: {url}
category: {category}
tags:
  - github
description: {description}

---
"""

@dataclass
class GithubTrending():
    output: str = "/srv/Base/Home/uglyboy/文档/Temp/Github 趋势.md"
    filename: str = "resource/github.db"
    summarizer: ReadmeSummarizer = field(init=False)
    category: Category = field(init=False)

    def __post_init__(self):
        self.summarizer = ReadmeSummarizer(self.filename)
        self.category = Category(self.filename)
        self.finished = KVCache(self.filename, "Finished", 30)
        self.config = KVCache(self.filename, "Config")

        self._repo_names = []
        self._repo_descriptions = {}

        date = self.config.get("Date").get("Date","")
        if date != datetime.now().strftime("%Y-%m-%d"):
            self._check_finished()

        text = GithubAPI.fetch_trending_file()
        for language in ["All Languages", "Python", "Typescript", "Rust", "Go", "Html", "Css"]:
            self._fetch_trending_repos(text, language)

        # 去重
        _set = set(self._repo_names)
        self._repo_names = list(_set)
        # 去除已经完成的
        self._remove_finished_repos()
        # 加载数据库
        self._data = self.summarizer._load(self._repo_names)

    def _check_finished(self):
        logger.info("Updating The Finished Repos...")
        #self._set_finished_with_favourite()
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
                description = self._repo_descriptions.get(name, "")
                category = self.category.cache.get(name).get(name, "Other")
                context = FRONT_MATTER.format(
                    description=description,
                    time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    url=f"https://www.github.com/{name}", category=category
                )
                context += "## " + name + "\n\n"
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
        index = [i for i in new_repo_names]
        #new_repo_names = self._repo_names

        for repo_name in index:
            readme = GithubAPI.fetch_readme(repo_name)
            if readme:
                if len(readme) > 40000:
                    readme = readme[:40000]
                readme_list.append(readme)
                description_list.append(self._repo_descriptions[repo_name])
            else:
                new_repo_names.remove(repo_name)

        datas = self.summarizer.run(
            new_repo_names, readme_list, description_list)

        self._data.update(datas)

    def _fetch_category(self):
        category_list = self.category.run(self._repo_names, self._data)
        return category_list

    def output_markdown(self, filename: str | None = None):
        if filename:
            self.output = filename
        # 增加循环，每次执行 20 个，避免并发太快
        repo_names = [i for i in self._repo_names]
        i = 0
        category_list = {}
        while  i*20 < len(repo_names):
            self._repo_names = repo_names[i*20:i*20+20]
            # 先更新数据库
            self._fetch_summarizer()
            # 更新分类，并获得分类结果
            _dict = self._fetch_category()
            for k,v in _dict.items():
                if k in category_list.keys():
                    category_list[k].extend(v)
                else:
                    category_list[k] = v
            i += 1
            #logger.info("Sleeping 5 seconds...")
            #sleep(5)
        self._repo_names = repo_names

        # 生成 markdown
        markdown_txt = FRONT_MATTER.format(
            description="Github Trending 项目解读",
            time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            url="", category="Github"
        )
        for category in ["AI", "后端", "前端", "资料", "其他"]:
            if category not in category_list.keys():
                continue
            markdown_txt += f"## {category}\n\n"
            for repo_name in category_list[category]:
                if repo_name not in self._data.keys():
                    continue
                name = urllib.parse.quote(repo_name, safe='')
                url = f"https://www.github.com/{repo_name}"
                markdown_txt += f"- [ ] [{repo_name}]({url}) - {self._repo_descriptions[repo_name]} [![](https://img.shields.io/badge/Click-Like-blue)]({name}) \n\n"
                for line in self._data[repo_name].split("\n"):
                    markdown_txt += f"> {line}\n"
                markdown_txt += "\n"

        File.save(self.output, markdown_txt)
