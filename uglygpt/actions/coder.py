#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from loguru import logger
from pathlib import Path
from typing import Optional

from uglygpt.actions.code import CodeWrite, CodeReviewer, TestWriter, CodeRewrite, Sandbox, TestFailedError
from uglygpt.base import File

@dataclass
class Coder:
    file_path: str
    request: str
    review_code: bool = False
    sandbox: Sandbox = field(default_factory=Sandbox)

    def __post_init__(self):
        self.writer = CodeWrite(self.file_path)
        self.reviewer = CodeReviewer(self.file_path)
        self.rewriter = CodeRewrite(self.file_path)
        self.tester = TestWriter(self.test_path)

    def gen_code(self) -> None:
        self._code = self.writer.run(self.request)
        self._code = self.reviewer.run(context = self.request, code = self.code)

    def change_code(self, extra: Optional[str] = None ) -> bool:
        if extra is None:
            extra = input("请输入你觉得需要修改的内容：")
            if extra == "":
                return False
        else:
            logger.info(extra)
        self._code = self.rewriter.run(context = f"函数原始需求：\n{self.request}", code = self.code, extra = extra)
        if self.review_code:
            self._code = self.reviewer.run(context = f"函数原始需求：\n{self.request}", code = self.code)
        return True


    def prepare_test(self) -> None:
        self.sandbox.init()
        self.sandbox.setup_venv()
        code = self.code
        sandbox_file_path = self.sandbox.prepare_test(self.file_path)
        context = f"---\n函数原始需求：\n{self.request}\n---\n 只写一个测试用例，只需要验证目标代码能否顺利执行即可，无需验证结果是否正确。"
        self.tester.run(context = context, code = code, working_dir = self.sandbox.dir, source_path = sandbox_file_path, test_path = self.test_path)

    def run_test(self) -> None:
        if not File.exists(self.test_path):
            self.prepare_test()

        retry = 0

        while True:
            try:
                retry += 1
                self.sandbox.run_test(self.test_path)
                break
            except TestFailedError as e:
                if retry > 3:
                    # 人工介入来提出修改意见
                    # TODO: 未来可以考虑使用人工智能来提出修改意见，包括上网搜索需要的信息。
                    if self.change_code():
                        retry = 0
                        if self.review_code:
                            self._code = self.reviewer.run(context = f"函数原始需求：\n{self.request}", code = self.code)
                        self.sandbox.prepare_test(self.file_path)
                    else:
                        break
                else:
                    debug = e.args[0]
                    self._code = self.rewriter.run(context = f"函数原始需求：\n{self.request}", code = self.code, extra = debug)
                    if self.review_code:
                        self._code = self.reviewer.run(context = f"函数原始需求：\n{self.request}", code = self.code)
                    self.sandbox.prepare_test(self.file_path)
            except Exception as e:
                raise
        if retry > 3:
            logger.error("代码依然无法通过测试，建议重新写代码。")

    @property
    def test_path(self) -> str:
        if not hasattr(self, "_test_path"):
            self._test_path = f"{self.sandbox.dir}/test_{Path(self.file_path).name}"
        return self._test_path

    @property
    def code(self) -> str:
        if not hasattr(self, "_code"):
            if File.exists(self.file_path):
                self._code = File.load(self.file_path)
            else:
                self.gen_code()
        return self._code