from dataclasses import dataclass, field
from pathlib import Path
from uglychain.storage import Storage

@dataclass
class FileStorage(Storage):
    file: str = "resource/temp"
    path: Path = field(init=False)

    def __post_init__(self):
        self.path = Path(self.file)

    def save(self, data: str):
        self.path.write_text(data)

    def load(self) -> str:
        return self.path.read_text()