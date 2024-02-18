#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime
import hashlib
import hmac
import base64
import json

import requests
from loguru import logger

from uglygpt.utils import config

@dataclass
class FeishuAPI:
    bot_webhook: str = config.feishu_webhook
    secret: str = config.feishu_secret

    @classmethod
    def post(cls, message: str|dict):
        timestamp = int(datetime.now().timestamp())
        if isinstance(message, dict):
            data = {
                "timestamp": timestamp,
                "sign": cls.gen_sign(timestamp),
                "msg_type": "interactive", # ctp_AA1MTiqzqdC4
                "card": json.dumps(message)
            }
        else:
            data = {
                "timestamp": timestamp,
                "sign": cls.gen_sign(timestamp),
                "msg_type": "text",
                "content": {
                    "text": message
                }
            }
        try:
            response = requests.post(
                cls.bot_webhook, headers={"Content-Type": "application/json"}, data=json.dumps(data))
            #response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            raise
        result = response.json()

        if result.get("code") != 0:
            logger.debug(result)
            logger.error(f"An error occurred: {result['msg']}")
            raise Exception(result['msg'])

    @classmethod
    def gen_sign(cls, timestamp):
        # 拼接timestamp和secret
        string_to_sign = '{}\n{}'.format(timestamp, cls.secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign