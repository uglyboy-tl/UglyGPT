from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from uglygpt.chains import LLMChain
from uglygpt.base import logger, WORKSPACE_ROOT

@dataclass
class Action(metaclass=ABCMeta):
    name: str = ""
    llm: LLMChain = field(default_factory=LLMChain)
    role: str = None
    filename: str = None

    def __post_init__(self):
        self.llm.llm.set_system(self.role)

    def _ask(self, *args, **kwargs) -> str:
        response = self.llm.run(*args, **kwargs)
        if self.filename:
            self._save(self.filename, response)
        return response

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    def _save(self, filename, data):
        file_path = WORKSPACE_ROOT / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(data)
        logger.debug(f"Saving file to {file_path}")

    def _load(self, filename=None):
        if not filename:
            if self.filename:
                filename = self.filename
            else:
                raise ValueError("filename is required")
        with open(WORKSPACE_ROOT / filename, "r") as f:
            data = f.read()
        return data