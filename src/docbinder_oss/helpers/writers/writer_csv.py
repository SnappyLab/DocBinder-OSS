import csv
import logging
from pathlib import Path
from typing import Any
from docbinder_oss.helpers.writers.base import Writer
from docbinder_oss.helpers.writers.helper_functions import flatten_file


class CSVWriter(Writer):
    """Writer for exporting data to CSV files."""

    def get_fieldnames(self, rows: list) -> list:
        fieldnames = set()
        for row in rows:
            fieldnames.update(row.keys())
        # Provider first, then the rest sorted
        return ["provider"] + sorted(f for f in fieldnames if f != "provider")

    def write(self, data: Any, file_path: str | Path | None = None) -> None:
        """
        Always flattens grouped dicts to a flat list for CSV export.
        """
        rows = []
        if isinstance(data, dict):
            for provider, items in data.items():
                for item in items:
                    rows.append(flatten_file(item, provider))
        elif isinstance(data, list):
            for item in data:
                provider = item.get("provider") if isinstance(item, dict) else getattr(item, "provider", None)
                rows.append(flatten_file(item, provider))
        else:
            return
        if not rows or not file_path:
            logging.warning("No data to write to CSV.")
            return
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.get_fieldnames(rows))
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
