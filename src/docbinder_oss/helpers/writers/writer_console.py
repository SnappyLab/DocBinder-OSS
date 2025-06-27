from pathlib import Path
from typing import Any
from docbinder_oss.helpers.writers.base import Writer


class ConsoleWriter(Writer):
    """Writer for pretty-printing data to the console using rich tables."""

    def write(self, data: Any, file_path: str | Path | None = None) -> None:
        from rich.table import Table

        table = Table(title="Files and Folders")
        table.add_column("Provider", justify="right", style="cyan", no_wrap=True)
        table.add_column("Id", style="magenta")
        table.add_column("Name", style="magenta")
        table.add_column("Kind", style="magenta")
        for provider, items in data.items() if isinstance(data, dict) else [("?", data)]:
            for item in items:
                if hasattr(item, "model_dump"):
                    item = item.model_dump()
                elif hasattr(item, "__dict__"):
                    item = dict(item.__dict__)
                table.add_row(
                    str(provider),
                    str(item.get("id", "")),
                    str(item.get("name", "")),
                    str(item.get("kind", "")),
                )
        print(table)
