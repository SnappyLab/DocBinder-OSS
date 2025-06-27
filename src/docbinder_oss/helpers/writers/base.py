from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Writer(ABC):
    """Abstract base writer class for exporting data."""

    @abstractmethod
    def write(self, data: Any, file_path: str | Path | None = None) -> None:
        pass
