#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass
from loguru import logger
from pathlib import Path
from typing import Optional

from uglychain import Model
from .utils import File
from uglygpt.worker.code import CodeWriter, CodeReviewer, CodeRewriter
from uglygpt.worker.code.file import FileStorage


@dataclass
class Coder:
    file_path: str
    request: str = ""
    review_code: bool = False
    model: Model = Model.YI

    def __post_init__(self):
        try:
            logger.add(
                f"logs/{File.path_to_filename(self.file_path)}.log",
                level="INFO",
                rotation="1 week",
                retention="10 days",
                compression="zip",
            )
        except Exception:
            logger.add(
                f"{Path(self.file_path).with_suffix('.log')}",
                level="INFO",
                rotation="1 week",
                retention="10 days",
            )

    def gen_code(self) -> None:
        if self.request == "":
            raise ValueError("request is empty, can not generate code.")
        logger.info(f"生成代码的原始需求：\n{self.request}")
        self._code = self.writer.run(self.request)
        self._code = self.reviewer.run(context=self.request, code=self.code)

    def enhance_code(self) -> None:
        self._code = self.reviewer.run(context=self.request, code=self.code)

    def change_code(self, extra: Optional[str] = None) -> bool:
        if extra is None:
            extra = input("请输入你觉得需要修改的内容：")
            if extra == "":
                return False
        else:
            logger.info(f"改进代码的具体要求\n{extra}")
        if self.request != "":
            context = f"函数原始需求：\n{self.request}"
        else:
            context = ""
        self._code = self.rewriter.run(context=context, code=self.code, extra=extra)
        if self.review_code:
            self._code = self.reviewer.run(context=context, code=self.code)
        return True

    @property
    def code(self) -> str:
        if not hasattr(self, "_code"):
            if File.exists(self.file_path):
                self._code = File.load(self.file_path)
            else:
                self.gen_code()
        return self._code

    @property
    def writer(self) -> CodeWriter:
        if not hasattr(self, "_writer"):
            self._writer = CodeWriter(model = self.model, storage=FileStorage(self.file_path))
        return self._writer

    @property
    def reviewer(self) -> CodeReviewer:
        if not hasattr(self, "_reviewer"):
            self._reviewer = CodeReviewer(model = self.model, storage=FileStorage(self.file_path))
        return self._reviewer

    @property
    def rewriter(self) -> CodeRewriter:
        if not hasattr(self, "_rewriter"):
            self._rewriter = CodeRewriter(model = self.model, storage=FileStorage(self.file_path))
        return self._rewriter
