import json
from pathlib import Path
from typing import Any
from docbinder_oss.helpers.writers.base import Writer
from docbinder_oss.helpers.writers.helper_functions import flatten_file


class JSONWriter(Writer):
    """Writer for exporting data to JSON files."""

    def write(self, data: Any, file_path: str | Path | None = None) -> None:
        """
        Always flattens grouped dicts to a flat list for JSON export.
        """
        flat = []
        if isinstance(data, dict):
            for provider, items in data.items():
                for item in items:
                    flat.append(flatten_file(item, provider))
        elif isinstance(data, list):
            for item in data:
                provider = item.get("provider") if isinstance(item, dict) else getattr(item, "provider", None)
                flat.append(flatten_file(item, provider))
        else:
            return
        if not file_path:
            return
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(flat, f, indent=2, ensure_ascii=False, default=str)
