"""Chain that runs an arbitrary python function."""
from typing import Callable, Dict, List
from dataclasses import dataclass, field

from uglygpt.chains.base import Chain

@dataclass
class TransformChain(Chain):
    """Chain transform chain output.

    Example:
        .. code-block:: python

            from langchain import TransformChain
            transform_chain = TransformChain(input_variables=["text"],
            output_variables["entities"], transform=func())
    """

    input_variables: List[str] = field(default_factory=list)
    output_variables: List[str] = field(default_factory=list)
    transform: Callable[[Dict[str, str]], Dict[str, str]] = field(default_factory=callable)

    @property
    def input_keys(self) -> List[str]:
        """Expect input keys.

        :meta private:
        """
        return self.input_variables

    @property
    def output_keys(self) -> List[str]:
        """Return output keys.

        :meta private:
        """
        return self.output_variables

    def _call(
        self,
        inputs: Dict[str, str],
    ) -> Dict[str, str]:
        return self.transform(inputs)