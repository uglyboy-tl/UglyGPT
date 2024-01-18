#!/usr/bin/env python3
# -*-coding:utf-8-*-
from http import HTTPStatus

class BadRequestError(Exception):
    pass

class Unauthorized(Exception):
    pass

class RequestLimitError(Exception):
    pass
