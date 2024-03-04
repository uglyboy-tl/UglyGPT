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
    SCENE,
)
from .schema import Characters, OutLine, Scene

ROLE = "你是一名通俗小说家，你需要按照指示一步一步的写出一部完整的小说。"


@dataclass
class Novel(BaseWorker):
    model: Model = Model.DEFAULT
    role: str = ROLE
    llm: LLM = field(init=False)

    @property
    def synopsis(self):
        if not hasattr(self, "_synopsis"):
            logger.info("生成剧情简介...")
            self.llm.prompt = SYNOPSIS
            self._synopsis = self.llm(self.input)
            logger.trace(f"剧情简介: {self._synopsis}")
        return self._synopsis

    @property
    def title(self):
        if not hasattr(self, "_title"):
            logger.info("生成小说名称...")
            self.llm.prompt = TITLE
            self._title = self.llm(synopsis=self.synopsis)
            logger.trace(f"小说名称: {self._title}")
        return self._title

    @property
    def theme(self):
        if not hasattr(self, "_theme"):
            logger.info("生成小说主题...")
            self.llm.prompt = THEME
            self._theme = self.llm(synopsis=self.synopsis)
            #self._flesh_out_theme()
            logger.trace(f"小说主题: {self._theme}")
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
            logger.info("生成小说设定...")
            self.llm.prompt = SETTING
            self._setting = self.llm(synopsis=self.synopsis)
            logger.trace(f"小说设定: {self._setting}")
        return self._setting

    @property
    def character(self) -> Characters:
        if not hasattr(self, "_character"):
            logger.info("生成小说角色...")
            self.llm.prompt = CHARACTER
            self.llm.response_model = Characters
            self._character = self.llm(synopsis=self.synopsis, theme=self.theme)
            logger.trace(f"小说角色: {self._character}")
        return self._character

    def _flesh_out_characters(self):
        for character in self.character:
            pass

    @property
    def outline(self) -> OutLine:
        if not hasattr(self, "_outline"):
            logger.info("生成小说大纲...")
            self.llm.prompt = OUTLINE
            self.llm.response_model = OutLine
            self._outline = self.llm(
                synopsis=self.synopsis, theme=self.theme, characters=self.character
            )
            logger.trace(f"小说大纲: {self._outline}")
        return self._outline

    def scenes(self):
        if not hasattr(self, "_scenes"):
            logger.info("生成小说场景...")
            self._scenes = []
            self.llm.prompt = SCENE
            self.llm.response_model = Scene
            summary = 'Beginning of story.'
            count = 1
            idx = 1
            for plot in self.outline.outline:
                print('\n\n',count,'of',len(self.outline.outline))
                count = count + 1
                print('\n\nPLOT BEAT:', plot)
                scenes = self.llm(plot = plot, summary = summary)
                self._scenes.extend(scenes.scenes)
                break
                prompt = open_file('prompt_summary.txt').replace('<<STORY>>', '%s %s' % (summary, text))
                summary = gpt3_completion(prompt, temp=0.5).replace('\s+',' ')
                print('\n\nSUMMARY:', summary)
        return self._scenes

    def run(self, input: str = ""):
        if not self.llm:
            self.llm = LLM(self.prompt, self.model, self.role)
        self.input = input
        logger.info("开始写小说...")
        logger.info(f"剧情简介: {self.synopsis}")
        logger.info(f"名称: {self.title}")
        logger.info(f"主题: {self.theme}")
        logger.info(f"设定: {self.setting}")
        logger.info(f"角色: {self.character}")
        logger.info(f"大纲: {self.outline}")
        logger.info(f"场景: {self.scenes}")