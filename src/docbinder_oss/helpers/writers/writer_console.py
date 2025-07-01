from pathlib import Path
from typing import Any
from rich.table import Table
from rich import print
from docbinder_oss.helpers.writers.base import Writer


class ConsoleWriter(Writer):
    """Writer for pretty-printing data to the console using rich tables."""

    def write(self, data: Any, file_path: str | Path | None = None) -> None:
        table = Table(title="Files and Folders")
        table.add_column("Provider", justify="right", style="cyan", no_wrap=True)
        table.add_column("Id", style="magenta")
        table.add_column("Name", style="magenta")
        table.add_column("Kind", style="magenta")
        for provider, items in data.items():
            for item in items:
                table.add_row(provider, item.id, item.name, item.kind)
        print(table)
