#!/usr/bin/env python3
# -*-coding:utf-8-*-

import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log, RetryError
from dataclasses import dataclass

from .base import Index

DUCKDUCKGO_SEARCH_API_URL = "https://api.duckduckgo.com"

@dataclass
class DuckDuckGo(Index):
    def search(self, query: str, n: int = Index.defaule_n) -> list[str]:
        try:
            response = self._send_request(query)
            json = response.json()
            results = json.get("Results", [])
            return [self._format(result) for result in results[:n]] if results else []
        except (ValueError, requests.RequestException, RetryError) as e:
            logger.error(f'Error occurred while sending request or parsing response: {e}')
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), before_sleep=before_sleep_log(logger, "WARNING")) # type: ignore
    def _send_request(self, query: str):
        params = {
            "q": query,
            "format": "json",
            "pretty": 1,
        }
        response = requests.get(DUCKDUCKGO_SEARCH_API_URL, params=params, timeout=5)
        response.raise_for_status()
        return response

    @classmethod
    def _format(cls, result: dict) -> str:
        title = result.get('Title', '')
        url = result.get('FirstURL', '')
        snippet = result.get('Text', '')
        if not all([title, url, snippet]):
            logger.error(f'Missing key in search result: {result}')
            raise KeyError('Missing key in search result')
        return f"[{title}]({url})\n> {snippet}"