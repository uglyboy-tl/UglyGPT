from abc import ABC, abstractmethod
from typing import Callable, Iterable, List, Optional, Any

from uglygpt.base import logger

class TextSplitter(ABC):
    def __init__(self, chunk_size: int, chunk_overlap: int, length_function: Callable[[str], int] = len):
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._length_function = length_function

    @abstractmethod
    def split_text(self, text: str):
        """Split text into multiple components."""
        pass

    def _join_docs(self, docs: List[str], separator: str) -> Optional[str]:
        text = separator.join(docs)
        text = text.strip()
        if text == "":
            return None
        else:
            return text

    def _merge_splits(self, splits: Iterable[str], separator: str) -> List[str]:
        # We now want to combine these smaller pieces into medium size
        # chunks to send to the LLM.
        separator_len = self._length_function(separator)

        docs = []
        current_doc: List[str] = []
        total = 0
        for d in splits:
            _len = self._length_function(d)
            if (
                total + _len + (separator_len if len(current_doc) > 0 else 0)
                > self._chunk_size
            ):
                if total > self._chunk_size:
                    logger.warn(
                        f"Created a chunk of size {total}, "
                        f"which is longer than the specified {self._chunk_size}"
                    )
                if len(current_doc) > 0:
                    doc = self._join_docs(current_doc, separator)
                    if doc is not None:
                        docs.append(doc)
                    # Keep on popping if:
                    # - we have a larger chunk than in the chunk overlap
                    # - or if we still have any chunks and the length is long
                    while total > self._chunk_overlap or (
                        total + _len +
                            (separator_len if len(current_doc) > 0 else 0)
                        > self._chunk_size
                        and total > 0
                    ):
                        total -= self._length_function(current_doc[0]) + (
                            separator_len if len(current_doc) > 1 else 0
                        )
                        current_doc = current_doc[1:]
            current_doc.append(d)
            total += _len + (separator_len if len(current_doc) > 1 else 0)
        doc = self._join_docs(current_doc, separator)
        if doc is not None:
            docs.append(doc)
        return docs

class CharacterTextSplitter(TextSplitter):
    """Implementation of splitting text that looks at characters."""

    def __init__(self, separator: str = "\n\n", **kwargs: Any):
        """Create a new TextSplitter."""
        super().__init__(**kwargs)
        self._separator = separator

    def split_text(self, text: str) -> List[str]:
        """Split incoming text and return chunks."""
        # First we naively split the large input into a bunch of smaller ones.
        if self._separator:
            splits = text.split(self._separator)
        else:
            splits = list(text)
        return self._merge_splits(splits, self._separator)

class RecursiveCharacterTextSplitter(TextSplitter):
    """Implementation of splitting text that looks at characters.

    Recursively tries to split by different characters to find one
    that works.
    """

    def __init__(self, separators: Optional[List[str]] = None, **kwargs: Any):
        """Create a new TextSplitter."""
        super().__init__(**kwargs)
        self._separators = separators or ["\n\n", "\n", " ", ""]

    def split_text(self, text: str) -> List[str]:
        """Split incoming text and return chunks."""
        final_chunks = []
        # Get appropriate separator to use
        separator = self._separators[-1]
        for _s in self._separators:
            if _s == "":
                separator = _s
                break
            if _s in text:
                separator = _s
                break
        # Now that we have the separator, split the text
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)
        # Now go merging things, recursively splitting longer texts.
        _good_splits = []
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                other_info = self.split_text(s)
                final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, separator)
            final_chunks.extend(merged_text)
        return final_chunks

class MarkdownTextSplitter(RecursiveCharacterTextSplitter):
    """Attempts to split the text along Markdown-formatted headings."""

    def __init__(self, **kwargs: Any):
        """Initialize a MarkdownTextSplitter."""
        separators = [
            # First, try to split along Markdown headings (starting with level 2)
            "\n## ",
            "\n### ",
            "\n#### ",
            "\n##### ",
            "\n###### ",
            # Note the alternative syntax for headings (below) is not handled here
            # Heading level 2
            # ---------------
            # End of code block
            "```\n\n",
            # Horizontal lines
            "\n\n***\n\n",
            "\n\n---\n\n",
            "\n\n___\n\n",
            # Note that this splitter doesn't handle horizontal lines defined
            # by *three or more* of ***, ---, or ___, but this is not handled
            "\n\n",
            "\n",
            " ",
            "",
        ]
        super().__init__(separators=separators, **kwargs)


class LatexTextSplitter(RecursiveCharacterTextSplitter):
    """Attempts to split the text along Latex-formatted layout elements."""

    def __init__(self, **kwargs: Any):
        """Initialize a LatexTextSplitter."""
        separators = [
            # First, try to split along Latex sections
            "\n\\chapter{",
            "\n\\section{",
            "\n\\subsection{",
            "\n\\subsubsection{",
            # Now split by environments
            "\n\\begin{enumerate}",
            "\n\\begin{itemize}",
            "\n\\begin{description}",
            "\n\\begin{list}",
            "\n\\begin{quote}",
            "\n\\begin{quotation}",
            "\n\\begin{verse}",
            "\n\\begin{verbatim}",
            ## Now split by math environments
            "\n\\begin{align}",
            "$$",
            "$",
            # Now split by the normal type of lines
            " ",
            "",
        ]
        super().__init__(separators=separators, **kwargs)


class PythonCodeTextSplitter(RecursiveCharacterTextSplitter):
    """Attempts to split the text along Python syntax."""

    def __init__(self, **kwargs: Any):
        """Initialize a PythonCodeTextSplitter."""
        separators = [
            # First, try to split along class definitions
            "\nclass ",
            "\ndef ",
            "\n\tdef ",
            # Now split by the normal type of lines
            "\n\n",
            "\n",
            " ",
            "",
        ]
        super().__init__(separators=separators, **kwargs)