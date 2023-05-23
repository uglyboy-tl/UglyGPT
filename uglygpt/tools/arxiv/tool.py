"""Tool for the Arxiv API."""

from dataclasses import dataclass, field

from uglygpt.tools.base import BaseTool
from uglygpt.utilities.arxiv import ArxivAPIWrapper

@dataclass
class ArxivQueryRun(BaseTool):
    """Tool that adds the capability to search using the Arxiv API."""

    name: str = "Arxiv"
    description: str = (
        "A wrapper around Arxiv.org "
        "Useful for when you need to answer questions about Physics, Mathematics, "
        "Computer Science, Quantitative Biology, Quantitative Finance, Statistics, "
        "Electrical Engineering, and Economics "
        "from scientific articles on arxiv.org. "
        "Input should be a search query."
    )
    api_wrapper: ArxivAPIWrapper = field(default_factory=ArxivAPIWrapper)

    def _run(
        self,
        query: str,
    ) -> str:
        """Use the Arxiv tool."""
        return self.api_wrapper.run(query)