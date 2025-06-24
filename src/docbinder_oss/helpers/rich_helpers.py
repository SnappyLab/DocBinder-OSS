from typing import List
from rich.table import Table


def create_rich_table(headers: List[str], rows: List[List[str]]) -> Table:
    """
    Create a Rich table with the given headers and rows.
    
    Args:
        headers (List[str]): The headers for the table.
        rows (List[List[str]]): The data rows for the table.
    
    Returns:
        Table: A Rich Table object.
    """
    table = Table(*headers, show_header=True, header_style="bold magenta")
    for row in rows:
        table.add_row(*row)
    return table