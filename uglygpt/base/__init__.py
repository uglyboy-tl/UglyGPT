#!/usr/bin/env python3
#-*-coding:utf-8-*-

from .config import config
from .logs import logger
from .singleton import singleton

__all__ = ['config', 'logger', 'singleton']