import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Union
from pydantic import BaseModel
from rich import print

import logging


logger = logging.getLogger(__name__)


class Writer(ABC):
    """Abstract base writer class."""

    @abstractmethod
    def write(self, data: Any, file_path: Union[None, str, Path]) -> None:
        """Write data to file."""
        pass


class MultiFormatWriter:
    """Factory writer that automatically detects format from file extension."""

    _writers = {
        ".csv": "CSVWriter",
        ".json": "JSONWriter",
    }

    @classmethod
    def write(cls, data: Any, file_path: Union[None, str, Path]) -> None:
        """Write data to file, format determined by extension."""
        if file_path is None:
            # If no file path is provided, write to console
            ConsoleWriter().write(data)
            return
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension not in cls._writers:
            raise ValueError(f"Unsupported format: {extension}")

        writer_class = globals()[cls._writers[extension]]
        writer = writer_class()
        writer.write(data, file_path)


class CSVWriter(Writer):
    def get_fieldnames(self, data: Dict[str, List[BaseModel]]) -> List[str]:
        fieldnames = next(iter(data.values()))[0].model_fields_set
        return ["provider", *fieldnames]

    def write(self, data: List[Dict], file_path: Union[str, Path]) -> None:
        if not data:
            logger.warning("No data to write to CSV.")
            return

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.get_fieldnames(data))
            writer.writeheader()
            for provider, items in data.items():
                for item in items:
                    item_dict = item.model_dump() if isinstance(item, BaseModel) else item
                    item_dict["provider"] = provider
                    writer.writerow(item_dict)


class JSONWriter(Writer):
    def write(self, data: Dict[str, List[BaseModel]], file_path: Union[str, Path]) -> None:
        data = {provider: [item.model_dump() for item in items] for provider, items in data.items()}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)


class ConsoleWriter(Writer):
    def write(self, data: Dict) -> None:
        from rich.table import Table

        table = Table(title="Files and Folders")
        table.add_column("Provider", justify="right", style="cyan", no_wrap=True)
        table.add_column("Id", style="magenta")
        table.add_column("Name", style="magenta")
        table.add_column("Kind", style="magenta")
        for provider, items in data.items():
            for item in items:
                table.add_row(provider, item.id, item.name, item.kind)
        print(table)
