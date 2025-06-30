from datetime import datetime
import re
import typer
from typing import Dict, List, Optional

from docbinder_oss.core.schemas import File
from docbinder_oss.helpers.config import load_config
from docbinder_oss.providers import create_provider_instance
from docbinder_oss.helpers.config import Config
from docbinder_oss.providers.base_class import BaseProvider
from docbinder_oss.helpers.writers.multiformat_writer import MultiFormatWriter

app = typer.Typer()


@app.command()
def search(
    name: Optional[str] = typer.Option(None, "--name", help="Regex to match file name"),
    owner: Optional[str] = typer.Option(None, "--owner", help="Owner/contributor/reader email address to filter"),
    updated_after: Optional[str] = typer.Option(None, "--updated-after", help="Last update after (ISO timestamp)"),
    updated_before: Optional[str] = typer.Option(None, "--updated-before", help="Last update before (ISO timestamp)"),
    created_after: Optional[str] = typer.Option(None, "--created-after", help="Created after (ISO timestamp)"),
    created_before: Optional[str] = typer.Option(None, "--created-before", help="Created before (ISO timestamp)"),
    min_size: Optional[int] = typer.Option(None, "--min-size", help="Minimum file size in KB"),
    max_size: Optional[int] = typer.Option(None, "--max-size", help="Maximum file size in KB"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider name to search in"),
    export_file: Optional[str] = typer.Option(
        None, "--export-file", help="Export file name (e.g. results.csv or results.json)"
    ),
):
    """Search for files or folders matching filters across all
    providers and export results as CSV or JSON. If --export-file is not provided, results are printed to the console."""

    config: Config = load_config()
    if not config.providers:
        typer.echo("No providers configured.")
        raise typer.Exit(code=1)

    current_files = {}
    for provider_config in config.providers:
        if provider and provider_config.name != provider:
            continue
        client: Optional[BaseProvider] = create_provider_instance(provider_config)
        if not client:
            typer.echo(f"Provider '{provider_config.name}' is not supported or not implemented.")
            raise typer.Exit(code=1)
        current_files[provider_config.name] = client.list_all_files()

    current_files = __filter_files(
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

    MultiFormatWriter.write(current_files, export_file)
    return


def __filter_files(
    files: Dict[str, List[File]],
    name=None,
    owner=None,
    updated_after=None,
    updated_before=None,
    created_after=None,
    created_before=None,
    min_size=None,
    max_size=None,
) -> Dict[str, List[File]]:
    """
    Filters a collection of files based on various criteria such as name, owner,
    modification/creation dates, and file size.

    Args:
        files (dict): A dictionary where keys are providers and values are lists of file objects.
        name (str, optional): A regex pattern to match file names (case-insensitive).
        owner (str, optional): An email address to match file owners.
        updated_after (str, optional): ISO format datetime string; only include files modified
        after this date.
        updated_before (str, optional): ISO format datetime string; only include files modified
        before this date.
        created_after (str, optional): ISO format datetime string; only include files created after
        this date.
        created_before (str, optional): ISO format datetime string; only include files created
        before this date.
        min_size (int, optional): Minimum file size in kilobytes (KB).
        max_size (int, optional): Maximum file size in kilobytes (KB).

    Returns:
        list: A list of file objects that match the specified filters.
    """

    def file_matches(file: File):
        if name and not re.search(name, file.name, re.IGNORECASE):
            return False
        if owner and (not file.owners or not any(owner in u.email_address for u in file.owners)):
            return False
        if updated_after:
            file_modified_time = __parse_dt(file.modified_time)
            updated_after_dt = __parse_dt(updated_after)
            if file_modified_time is None or updated_after_dt is None or file_modified_time < updated_after_dt:
                return False
        if updated_before:
            file_modified_time = __parse_dt(file.modified_time)
            updated_before_dt = __parse_dt(updated_before)
            if file_modified_time is None or updated_before_dt is None or file_modified_time > updated_before_dt:
                return False
        if created_after:
            file_created_time = __parse_dt(file.created_time)
            created_after_dt = __parse_dt(created_after)
            if file_created_time is None or created_after_dt is None or file_created_time < created_after_dt:
                return False
        if created_before:
            file_created_time = __parse_dt(file.created_time)
            created_before_dt = __parse_dt(created_before)
            if file_created_time is not None and created_before_dt is not None and file_created_time > created_before_dt:
                return False
        if min_size and file.size < min_size:
            return False
        if max_size and file.size > max_size:
            return False
        return True

    filtered = {}
    for provider, file_list in files.items():
        filtered[provider] = [file for file in file_list if file_matches(file)]
    return filtered


def __parse_dt(val):
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(val)
    except Exception as e:
        typer.echo(f"Failed to parse datetime from value: {val} with error: {e}", err=True)
        raise ValueError(f"Invalid datetime format: {val}") from e
