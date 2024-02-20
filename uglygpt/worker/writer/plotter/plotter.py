from dataclasses import dataclass, field

from loguru import logger

from uglychain import LLM, Model, BaseWorker

from .prompt import (
    SYNOPSIS,
    TITLE,
    THEME,
    THEME_LIGHT,
    THEME_DARK,
    THEME_UNDERSTAND,
    SETTING,
    CHARACTER,
    OUTLINE,
)
from .schema import Characters, OutLine

ROLE = "你是一名通俗小说家，你需要按照指示一步一步的写出一部完整的小说。"


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
            #self._flesh_out_theme()
        return self._theme

    def _flesh_out_theme(self):
        self.llm.prompt = THEME_LIGHT
        light = self.llm(theme=self.theme)
        self.llm.prompt = THEME_DARK
        dark = self.llm(theme=self.theme)
        self.llm.prompt = THEME_UNDERSTAND
        understand = self.llm(theme=self.theme)
        self._theme = f"{self.theme}\n\n{light}\n\n{dark}\n\n{understand}"

    @property
    def setting(self):
        if not hasattr(self, "_setting"):
            self.llm.prompt = SETTING
            self._setting = self.llm(synopsis=self.synopsis)
        return self._setting

    @property
    def character(self) -> Characters:
        if not hasattr(self, "_character"):
            self.llm.prompt = CHARACTER
            self.llm.response_model = Characters
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
        #logger.info(f"Title: {self.title}")
        logger.info(f"Theme: {self.theme}")
        # logger.info(f"Setting: {self.setting}")
        # logger.info(f"Character: {self.character}")
        # logger.info(f"Outline: {self.outline}")