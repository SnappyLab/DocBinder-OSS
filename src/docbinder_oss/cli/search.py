from datetime import datetime
import re
import typer
from rich import print as rich_print
from typing import Optional

from docbinder_oss.helpers.config import Config
from docbinder_oss.helpers.rich_helpers import create_rich_table
from docbinder_oss.services.base_class import BaseProvider

app = typer.Typer()


@app.command()
def search(
    name: Optional[str] = typer.Option(None, "--name", help="Regex to match file name"),
    owner: Optional[str] = typer.Option(
        None, "--owner", help="Owner/contributor/reader email address to filter"
    ),
    updated_after: Optional[str] = typer.Option(
        None, "--updated-after", help="Last update after (ISO timestamp)"
    ),
    updated_before: Optional[str] = typer.Option(
        None, "--updated-before", help="Last update before (ISO timestamp)"
    ),
    created_after: Optional[str] = typer.Option(
        None, "--created-after", help="Created after (ISO timestamp)"
    ),
    created_before: Optional[str] = typer.Option(
        None, "--created-before", help="Created before (ISO timestamp)"
    ),
    min_size: Optional[int] = typer.Option(None, "--min-size", help="Minimum file size in KB"),
    max_size: Optional[int] = typer.Option(None, "--max-size", help="Maximum file size in KB"),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="Provider name to search in"
    ),
    export_format: str = typer.Option(
        None, "--export-format", help="Export format: csv or json", show_default=True
    ),
):
    """Search for files or folders matching filters across all
    providers and export results as CSV or JSON."""
    import csv
    import json
    from docbinder_oss.helpers.config import load_config
    from docbinder_oss.services import create_provider_instance
    
    # 1 Load documents with filter "provider"
    # 2 Filter the documents based on the provided filters
    # 3 Export results to CSV or JSON
    
    config: Config = load_config()
    if not config.providers:
        typer.echo("No providers configured.")
        raise typer.Exit(code=1)
    
    current_files = {}
    for provider_config in config.providers:
        if provider and provider_config.name != provider:
            continue
        client: BaseProvider = create_provider_instance(provider_config)
        if not client:
            typer.echo(f"Provider '{provider_config.name}' is not supported or not implemented.")
            raise typer.Exit(code=1)
        current_files[provider_config.name] = client.list_all_files()
    
    rich_print(current_files["my_google_drive"])
    
    current_files = filter_files(
        current_files,
        name=name,
        owner=owner,
        updated_after=updated_after,
        updated_before=updated_before,
        created_after=created_after,
        created_before=created_before,
        min_size=min_size,
        max_size=max_size,
    )
    rich_print(current_files["my_google_drive"])
    if not export_format:
        table = create_rich_table(
            headers=["Provider", "Name", "ID", "Size", "Created Time", "Modified Time"],
            rows=current_files
        )
        rich_print(table)
        return

def filter_files(
    files,
    name=None,
    owner=None,
    updated_after=None,
    updated_before=None,
    created_after=None,
    created_before=None,
    min_size=None,
    max_size=None,
):
    results = []
    
    for file in files:
        if name and not re.search(name, file.name, re.IGNORECASE):
            continue
        if owner and not any(owner in u.email_address for u in file.owners):
            continue
        if updated_after and file.modified_time < datetime.fromisoformat(updated_after):
            continue
        if updated_before and file.modified_time > datetime.fromisoformat(updated_before):
            continue
        if created_after and file.created_time < datetime.fromisoformat(created_after):
            continue
        if created_before and file.created_time > datetime.fromisoformat(created_before):
            continue
        if min_size and file.size < min_size * 1024:
            continue
        if max_size and file.size > max_size * 1024:
            continue

        results.append(file)

    return results