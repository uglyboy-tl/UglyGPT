#!/usr/bin/env python3
# -*-coding:utf-8-*-

import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed
from dataclasses import dataclass

from uglygpt.base import config
from .base import Index

BING_SEARCH_API_URL = 'https://api.bing.microsoft.com/v7.0/search'

@dataclass
class BingSearch(Index):
    def __post_init__(self):
        assert hasattr(config, 'bing_subscription_key'), 'Bing subscription key not found in config'
        assert isinstance(config.bing_subscription_key, str), 'Bing subscription key should be a string'
        assert config.bing_subscription_key, 'Bing subscription key should not be empty'

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def _send_request(self, query: str, n: int):
        response = requests.get(
            BING_SEARCH_API_URL,
            headers={'Ocp-Apim-Subscription-Key': config.bing_subscription_key},
            params={'q': query, 'count': n}
        )
        response.raise_for_status()
        return response

    def search(self, query: str, n: int) -> list[str]:
        response = self._send_request(query, n)
        try:
            json = response.json()
            results = json.get('webPages', {}).get('value', [])
            return [self._format(result) for result in results[:n]] if results else []
        except requests.exceptions.RequestException as e:
            logger.error(f'Error occurred while sending request to Bing: {e}')
            raise e

    @classmethod
    def _format(cls, result: dict) -> str:
        if not all([result.get('name'), result.get('url'), result.get('snippet')]):
            logger.error(f'Missing key in search result: {result}')
            raise KeyError('Missing key in search result')
        return f"[{result.get('name')}]({result.get('url')})\n> {result.get('snippet')}"