#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from loguru import logger

from ..base import Action
from uglychain import LLM

ROLE = """
假设你是一名经验丰富的技术文档撰写人员，你的工作是撰写技术文档。你即将完成的工作是根据提供的信息和要求，针对目标课题（可能是一个软件、一个插件、一个开源项目之类），撰写一份技术文档。具体要求如下：

- 技术文档的内容包括但不限于：项目的概述、安装部署、使用说明等。
- 在概述部分，你需要综述软件的用途，优缺点，特色等。也可以补充介绍一些和软件相关的配套工具。
- 在安装部署部分，你需要优先介绍通过包管理器安装的方式（只需要提供 Linux 平台的安装方式即可），如果是软件则无需提供docker的方式；如果是服务则尽量选择通过 docker 使用的方法。安装的方式尽量少不要超过3种。如果介绍的是插件，则可以介绍如何安装插件，或者如何使用插件。不同的方式可以分成不同的小节，使用三级标题即可。如有需要，可以提供相关的配置文件样例。如果安装流程较为复杂，可以只提供安装指南的链接。
- 在使用说明部分，你需要简要介绍项目最主要的使用方法，如果有必要，可以提供一些使用示例；尤其是可以补充一些特殊的使用方法或者容易被忽视的小细节。不用过于详细，只要能够让用户快速上手即可。
- 注意：请用中文生成文档，不要使用英文。

请按照以下示例格式返回你的结果：
格式示例：
```markdown
---
description: {项目内容描述}
date created: 2022-02-20 09:08
url: {项目地址}
category: other
tags:
  - 项目相关的标签
  - ...
date modified: 2023-03-03 09:59
---

## 概览
{项目概览}
## 安装部署
{项目安装部署的方法}
## 使用说明
{项目使用说明}
```
---
"""

PROMPT_TEMPLATE = """
# Context
## Original Requirements
{requirements}

time now: {time_now}
"""

@dataclass
class Technical(Action):
    role: str = ROLE
    llm: LLM = field(init=False)
    name: str = "技术文档撰写"

    def __post_init__(self):
        self.llm = LLM(PROMPT_TEMPLATE, "chatgpt", self.role)
        return super().__post_init__()

    def run(self, *args, **kwargs):
        logger.info(f"正在执行 {self.name} 的任务...")
        response = self.ask(*args, **kwargs)
        self._save(response)
        return response
