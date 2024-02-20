from dataclasses import dataclass, field
from typing import List

from pydantic import BaseModel, Field

from loguru import logger

from uglychain import LLM, Model, BaseWorker

ROLE = "你是一名通俗小说家，你需要按照指示一步一步的写出一部完整的小说。"

SYNOPSIS = """Brainstorm an extremely long complete, detailed synopsis for a story with the following appeal terms:

{input}


Extremely long and highly detailed complete plot synopsis with beginning, middle, and end.
Translate the output into Chinese if it is not already in Chinese.

BEGINNING:"""
TITLE = """Come up with the perfect title for the following premise.  The title should be pithy, catchy, and memorable.
Translate the title into Chinese if it is not already in Chinese.

PREMISE: {synopsis}

UNIQUE PERFECT TITLE:
"""

THEME = """Describe the theme of the following story in a few sentences. What is the universal truth elucidated by this story?
Translate the output into Chinese if it is not already in Chinese.

STORY: {synopsis}

UNIVERSAL TRUTH:
"""

SETTING = """Use your imagination to brainstorm details about the setting. Think about history, culture, atmosphere, religion, politics, and so on.
Translate the output into Chinese if it is not already in Chinese.

STORY: {synopsis}

BRAINSTORM SETTING IDEAS:
"""

CHARACTER = """Brainstorm original characters for the following story. List names, backstories, and personalities. Vividly depict all characters. Invent names if necessary.
Translate the output into Chinese if it is not already in Chinese.

STORY: {synopsis}

UNIVERSAL TRUTH: {theme}

LIST OF CHARACTERS:
"""

OUTLINE = """Brainstorm a highly detailed plot outline with at least 12 plot beats. List all the story beats in sequence and describe each plot element with a few sentences.
Translate the output into Chinese if it is not already in Chinese.

STORY: {synopsis}

THEME: {theme}

CHARACTERS:
{characters}

LONG DETAILED PLOT OUTLINE:
"""


class OutLine(BaseModel):
    outline: List[str] = Field(
        ..., description="list of outline, around 12 plot beats."
    )


@dataclass
class Novel(BaseWorker):
    model: Model = Model.DEFAULT
    role: str = ROLE
    llm: LLM = field(init=False)

    @property
    def synopsis(self):
        if not hasattr(self, "_synopsis"):
            self.llm.prompt = SYNOPSIS
            self._synopsis = self.llm(self.input)
        return self._synopsis

    @property
    def title(self):
        if not hasattr(self, "_title"):
            self.llm.prompt = TITLE
            self._title = self.llm(synopsis=self.synopsis)
        return self._title

    @property
    def theme(self):
        if not hasattr(self, "_theme"):
            self.llm.prompt = THEME
            self._theme = self.llm(synopsis=self.synopsis)
        return self._theme

    @property
    def setting(self):
        if not hasattr(self, "_setting"):
            self.llm.prompt = SETTING
            self._setting = self.llm(synopsis=self.synopsis)
        return self._setting

    @property
    def character(self):
        if not hasattr(self, "_character"):
            self.llm.prompt = CHARACTER
            self._character = self.llm(synopsis=self.synopsis, theme=self.theme)
        return self._character

    @property
    def outline(self) -> OutLine:
        if not hasattr(self, "_outline"):
            self.llm.prompt = OUTLINE
            self.llm.response_model = OutLine
            self._outline = self.llm(
                synopsis=self.synopsis, theme=self.theme, characters=self.character
            )
        return self._outline

    def run(self, input: str = ""):
        if not self.llm:
            self.llm = LLM(self.prompt, self.model, self.role)
        self.input = input
        logger.info("Start writing novel...")
        logger.info(f"Synopsis: {self.synopsis}")
        logger.info(f"Title: {self.title}")
        logger.info(f"Theme: {self.theme}")
        logger.info(f"Setting: {self.setting}")
        logger.info(f"Character: {self.character}")
        logger.info(f"Outline: {self.outline}")


if __name__ == "__main__":
    novel = Novel()
    novel.run(
        "一个关于人族和虫族的战争，人族的女王被虫族的女王抓住，虫族女王想要用人族女王的身体来孵化自己的后代。"
    )
