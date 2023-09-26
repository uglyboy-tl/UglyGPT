#!/usr/bin/env python3
# -*-coding:utf-8-*-

import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed, before_sleep_log, RetryError
from dataclasses import dataclass

from .base import Index

WIKIPEDIA_SEARCH_API_URL = 'https://en.wikipedia.org/w/api.php'

@dataclass
class WikipediaSearch(Index):
    def search(self, query: str, n: int = Index.default_n) -> list[str]:
        try:
            response = self._send_request(query, n)
            json = response.json()
            results = json.get('query', {}).get('search', [])
            return [self._format(result) for result in results[:n]] if results else []
        except (ValueError, requests.RequestException, RetryError) as e:
            logger.error(f'Error occurred while sending request or parsing response: {e}')
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), before_sleep=before_sleep_log(logger, "WARNING")) # type: ignore
    def _send_request(self, query: str, n: int):
        response = requests.get(
            WIKIPEDIA_SEARCH_API_URL,
            params={
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'srlimit': n
            },
            timeout=5
        )
        response.raise_for_status()
        return response

    @classmethod
    def _format(cls, result: dict) -> str:
        if not all([result.get('title'), result.get('snippet')]):
            logger.error(f'Missing key in search result: {result}')
            raise KeyError('Missing key in search result')
        url = WIKIPEDIA_SEARCH_API_URL + '?title=' + result.get('title').replace(' ', '_') + '&action=view' # type: ignore
        return f"[{result.get('title')}]({url})\n> {result.get('snippet')}"