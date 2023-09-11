#!/usr/bin/env python3
#-*-coding:utf-8-*-

import os
from loguru import logger as lg
from dataclasses import dataclass

from .singleton import singleton
from .config import config

@singleton
@dataclass
class AppLogger:
    app_logger = lg

    def set_logger(self, filename, filter_type=None, level='DEBUG'):
        """
        :param filename: 日志文件名
        :param filter_type: 日志过滤，如：将日志级别为ERROR的单独记录到一个文件中
        :param level: 日志级别设置
        :return:
        """

        dic = dict(
            sink=self.get_log_path(filename),
            rotation='500 MB',
            retention='30 days',
            format="{time}|{level}|{message}",
            encoding='utf-8',
            level=level,
            enqueue=True,
        )
        if filter_type:
            dic["filter"] = lambda x: filter_type in str(x['level']).upper()
        self.app_logger.add(**dic)
        return self.app_logger

    @property
    def get_logger(self):
        return self.app_logger

    @staticmethod
    def get_log_path(filename):
        log_path = os.path.join(config.BASE_LOG_DIR, filename)
        return log_path

    def trace(self, msg):
        self.app_logger.trace(msg)

    def debug(self, msg):
        self.app_logger.debug(msg)

    def info(self, msg):
        self.app_logger.info(msg)

    def success(self, msg):
        self.app_logger.success(msg)

    def warning(self, msg):
        self.app_logger.warning(msg)

    def error(self, msg):
        self.app_logger.error(msg)

    def critical(self, msg):
        self.app_logger.critical(msg)




logger = AppLogger()
logger.set_logger('error.log', filter_type='ERROR')
logger.set_logger('service.log', filter_type='INFO', level='INFO')