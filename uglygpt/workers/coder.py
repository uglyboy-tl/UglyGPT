#!/usr/bin/env python3
# -*-coding:utf-8-*-

from dataclasses import dataclass, field
from loguru import logger
from pathlib import Path
from typing import Optional

from uglygpt.actions.code import CodeWrite, CodeReviewer, TestWriter, CodeRewrite
from uglygpt.workers.sandbox import Sandbox, TestFailedError
from uglygpt.base import File

@dataclass
class Coder:
    file_path: str
    request: str = ""
    review_code: bool = False
    sandbox: Sandbox = field(default_factory=Sandbox)

    def __post_init__(self):
        self.writer = CodeWrite(self.file_path)
        self.reviewer = CodeReviewer(self.file_path)
        self.rewriter = CodeRewrite(self.file_path)
        self.tester = TestWriter(self.test_path)
        self.unittester = TestWriter(self.unittest_path)
        logger.add(f"logs/{File.path_to_filename(self.file_path)}.log", level="INFO", rotation="1 week", retention="10 days", compression="zip")

    def gen_code(self) -> None:
        if self.request == "":
            raise ValueError("request is empty, can not generate code.")
        logger.info(f"生成代码的原始需求：\n{self.request}")
        self._code = self.writer.run(self.request)
        self._code = self.reviewer.run(context = self.request, code = self.code)

    def enhance_code(self) -> None:
        self._code = self.reviewer.run(context = self.request, code = self.code)

    def change_code(self, extra: Optional[str] = None ) -> bool:
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
        self._code = self.rewriter.run(context = context, code = self.code, extra = extra)
        if self.review_code:
            self._code = self.reviewer.run(context = context, code = self.code)
        return True

    def gen_unittest(self) -> None:
        if self.request != "":
            context = f"---\n函数原始需求：\n{self.request}\n---"
        else:
            context = ""
        self.unittester.run(context = f"{context}", code = self.code, working_dir = str(File.WORKSPACE_ROOT), source_path = self.file_path, test_path = self.unittest_path)
        if self.review_code:
            agent = CodeReviewer(self.unittest_path)
            agent.run(context = f"这是一个unittest测试文件\n{context}", code = agent._load())

    def prepare_debug(self) -> None:
        self.sandbox.init()
        self.sandbox.setup_venv()
        code = self.code
        sandbox_file_path = self.sandbox.prepare_test(self.file_path)
        context = f"---\n函数原始需求：\n{self.request}\n---\n 所有的测试用例只需要验证目标代码中的函数或者类的方法能否顺利执行即可，无需验证结果是否正确。"
        working_path = Path(self.sandbox.dir)
        source_path = Path(sandbox_file_path).relative_to(working_path)
        test_path = Path(self.test_path).relative_to(working_path)
        self.tester.run(context = context, code = code, working_dir = self.sandbox.dir, source_path = str(source_path), test_path = str(test_path))
        if self.review_code:
            agent = CodeReviewer(self.test_path)
            agent.run(context =f"这是一个unittest测试文件\n{context}", code = agent._load())

    def run_debug(self) -> None:
        if not File.exists(self.test_path):
            self.prepare_debug()

        if self.request != "":
            context = f"函数原始需求：\n{self.request}"
        else:
            context = ""

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
                            self._code = self.reviewer.run(context = context, code = self.code)
                        self.sandbox.prepare_test(self.file_path)
                    else:
                        break
                else:
                    debug = e.args[0]
                    self._code = self.rewriter.run(context = context, code = self.code, extra = debug)
                    if self.review_code:
                        self._code = self.reviewer.run(context = context, code = self.code)
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
    def unittest_path(self) -> str:
        if not hasattr(self, "_unittest_path"):
            self._unittest_path = f"tests/test_{Path(self.file_path).name}"
        return self._unittest_path

    @property
    def code(self) -> str:
        if not hasattr(self, "_code"):
            if File.exists(self.file_path):
                self._code = File.load(self.file_path)
            else:
                self.gen_code()
        return self._code