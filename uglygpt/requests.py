"""Lightweight wrapper around requests library, with async support."""
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

@dataclass
class Requests:
    """Wrapper around requests to handle auth and async.

    The main purpose of this wrapper is to handle authentication (by saving
    headers) and enable easy async methods on the same base object.
    """

    headers: Optional[Dict[str, str]] = None

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """GET the URL and return the text."""
        return requests.get(url, headers=self.headers, **kwargs)

    def post(self, url: str, data: Dict[str, Any], **kwargs: Any) -> requests.Response:
        """POST to the URL and return the text."""
        return requests.post(url, json=data, headers=self.headers, **kwargs)

    def patch(self, url: str, data: Dict[str, Any], **kwargs: Any) -> requests.Response:
        """PATCH the URL and return the text."""
        return requests.patch(url, json=data, headers=self.headers, **kwargs)

    def put(self, url: str, data: Dict[str, Any], **kwargs: Any) -> requests.Response:
        """PUT the URL and return the text."""
        return requests.put(url, json=data, headers=self.headers, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> requests.Response:
        """DELETE the URL and return the text."""
        return requests.delete(url, headers=self.headers, **kwargs)

@dataclass
class TextRequestsWrapper:
    """Lightweight wrapper around requests library.

    The main purpose of this wrapper is to always return a text output.
    """

    headers: Optional[Dict[str, str]] = None

    @property
    def requests(self) -> Requests:
        return Requests(headers=self.headers)

    def get(self, url: str, **kwargs: Any) -> str:
        """GET the URL and return the text."""
        return self.requests.get(url, **kwargs).text

    def post(self, url: str, data: Dict[str, Any], **kwargs: Any) -> str:
        """POST to the URL and return the text."""
        return self.requests.post(url, data, **kwargs).text

    def patch(self, url: str, data: Dict[str, Any], **kwargs: Any) -> str:
        """PATCH the URL and return the text."""
        return self.requests.patch(url, data, **kwargs).text

    def put(self, url: str, data: Dict[str, Any], **kwargs: Any) -> str:
        """PUT the URL and return the text."""
        return self.requests.put(url, data, **kwargs).text

    def delete(self, url: str, **kwargs: Any) -> str:
        """DELETE the URL and return the text."""
        return self.requests.delete(url, **kwargs).text


# For backwards compatibility
RequestsWrapper = TextRequestsWrapper