#!/usr/bin/env python3
# -*-coding:utf-8-*-

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from typing import Optional

from uglygpt.chains import LLMChain
from uglygpt.base import File


@dataclass
class Action(ABC):
    """Base class for actions.

    Attributes:
        role: The role of the action.
        filename: The filename associated with the action.
        llm: The LLMChain object used for the action.
    """
    filename: Optional[str] = None
    role: Optional[str] = None
    llm: LLMChain = field(default_factory=LLMChain)

    def __post_init__(self):
        """Post initialization method.

        Sets the system of the LLMChain object if a role is provided.
        """
        if self.role:
            self.llm.llm.set_system(self.role)

    def ask(self, *args, **kwargs) -> str:
        """Ask a question to the LLMChain object.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The response from the LLMChain object.
        """
        response = self.llm(*args, **kwargs)
        return response

    def _save(self, data: Optional[str] = None, filename: Optional[str] = None):
        """Save data to a file.

        Args:
            data: The data to be saved.
            filename: The filename to save the data to.

        Raises:
            ValueError: If data is not provided and no default filename is set.
        """
        if not filename:
            if self.filename:
                filename = self.filename
            else:
                return
        if not data:
            raise ValueError("data is required")
        File.save(filename, data)

    def _load(self, filename: Optional[str] = None):
        """Load data from a file.

        Args:
            filename: The filename to load the data from.

        Returns:
            The loaded data.

        Raises:
            ValueError: If no filename is provided and no default filename is set.
        """
        if not filename:
            if self.filename:
                filename = self.filename
            else:
                raise ValueError("filename is required")
        data = File.load(filename)
        return data

    def _parse(self, text: str):
        """Parse text.

        Args:
            text: The text to be parsed.

        Returns:
            The parsed text.
        """
        return text

    @abstractmethod
    def run(self, *args, **kwargs):
        """Abstract method to be implemented by subclasses.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        pass
