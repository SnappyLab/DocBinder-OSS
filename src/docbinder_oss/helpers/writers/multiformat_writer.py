from pathlib import Path
from typing import Dict, List

from docbinder_oss.core.schemas import File
from docbinder_oss.helpers.writers.base import Writer
from docbinder_oss.helpers.writers.writer_console import ConsoleWriter
from docbinder_oss.helpers.writers.writer_csv import CSVWriter
from docbinder_oss.helpers.writers.writer_json import JSONWriter


class MultiFormatWriter:
    """
    Factory writer that automatically detects format from file extension or format string.
    If file_path is None, prints to console.
    """

    _writers = {
        ".csv": CSVWriter,
        ".json": JSONWriter,
        "csv": CSVWriter,
        "json": JSONWriter,
    }

    @classmethod
    def write(cls, data: Dict[str, List[File]], file_path: str | None = None) -> None:
        if not file_path:
            ConsoleWriter().write(data)
            return
        extension = Path(file_path).suffix.lower()
        # Use extension or fallback to format string
        writer_key = extension if extension in cls._writers else file_path.lower()
        if writer_key not in cls._writers:
            raise ValueError(f"Unsupported format: {file_path}")
        writer_class = cls._writers[writer_key]
        writer: Writer = writer_class()
        writer.write(data, file_path)
 