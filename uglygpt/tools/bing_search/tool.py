"""Tool for the Bing search API."""
from dataclasses import dataclass, field

from uglygpt.tools.base import BaseTool
from uglygpt.utilities.bing_search import BingSearchAPIWrapper

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