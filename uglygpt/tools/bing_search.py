"""Tool for the Bing search API."""
import os

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from uglygpt.tools.base import BaseTool

import requests

@dataclass
class BingSearchAPIWrapper():
    """Wrapper for Bing Search API.

    In order to set this up, follow instructions at:
    https://levelup.gitconnected.com/api-tutorial-how-to-use-bing-web-search-api-in-python-4165d5592a7e
    """

    bing_subscription_key: str = os.environ.get("BING_SUBSCRIPTION_KEY")
    bing_search_url: str = os.environ.get("BING_SEARCH_URL")
    k: int = 10

    def _bing_search_results(self, search_term: str, count: int) -> List[dict]:
        headers = {"Ocp-Apim-Subscription-Key": self.bing_subscription_key}
        params = {
            "q": search_term,
            "count": count,
            "textDecorations": True,
            "textFormat": "HTML",
        }
        response = requests.get(
            self.bing_search_url, headers=headers, params=params  # type: ignore
        )
        response.raise_for_status()
        search_results = response.json()
        return search_results["webPages"]["value"]

    def run(self, query: str) -> str:
        """Run query through BingSearch and parse result."""
        snippets = []
        results = self._bing_search_results(query, count=self.k)
        if len(results) == 0:
            return "No good Bing Search Result was found"
        for result in results:
            snippets.append(result["snippet"])

        return " ".join(snippets)

    def results(self, query: str, num_results: int) -> List[Dict]:
        """Run query through BingSearch and return metadata.

        Args:
            query: The query to search for.
            num_results: The number of results to return.

        Returns:
            A list of dictionaries with the following keys:
                snippet - The description of the result.
                title - The title of the result.
                link - The link to the result.
        """
        metadata_results = []
        results = self._bing_search_results(query, count=num_results)
        if len(results) == 0:
            return [{"Result": "No good Bing Search Result was found"}]
        for result in results:
            metadata_result = {
                "snippet": result["snippet"],
                "title": result["name"],
                "link": result["url"],
            }
            metadata_results.append(metadata_result)

        return metadata_results

@dataclass
class BingSearchRun(BaseTool):
    """Tool that adds the capability to query the Bing search API."""

    name: str = "Bing Search"
    description: str = (
        "A wrapper around Bing Search. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query."
    )
    api_wrapper: BingSearchAPIWrapper = field(default_factory=BingSearchAPIWrapper)

    def _run(
        self,
        query: str,
    ) -> str:
        """Use the tool."""
        return self.api_wrapper.run(query)

@dataclass
class BingSearchResults(BaseTool):
    """Tool that has capability to query the Bing Search API and get back json."""
    name: str = "Bing Search Results JSON"
    description: str = (
        "A wrapper around Bing Search. "
        "Useful for when you need to answer questions about current events. "
        "Input should be a search query. Output is a JSON array of the query results"
    )
    num_results: int = 4
    api_wrapper: BingSearchAPIWrapper = field(default_factory=BingSearchAPIWrapper)

    def _run(
        self,
        query: str,
    ) -> str:
        """Use the tool."""
        return str(self.api_wrapper.results(query, self.num_results))