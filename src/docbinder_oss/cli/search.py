from datetime import datetime
import re
import typer
from rich import print as rich_print
from typing import Optional
import csv
import json

from docbinder_oss.core.schemas import File
from docbinder_oss.helpers.config import load_config
from docbinder_oss.providers import create_provider_instance
from docbinder_oss.helpers.config import Config
from docbinder_oss.helpers.rich_helpers import create_rich_table
from docbinder_oss.providers.base_class import BaseProvider
from docbinder_oss.helpers.path_utils import build_id_to_item, get_full_path, build_all_full_paths

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
        client: Optional[BaseProvider] = create_provider_instance(provider_config)
        if not client:
            typer.echo(f"Provider '{provider_config.name}' is not supported or not implemented.")
            raise typer.Exit(code=1)
        current_files[provider_config.name] = client.list_all_files()
    
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
    
    if not export_format:
        typer.echo(current_files)
        return
    
    elif export_format.lower() == "csv":
        __write_csv(filtered_files_by_provider, "search_results.csv")
        typer.echo("Results written to search_results.csv")
    elif export_format.lower() == "json":
        __write_json(filtered_files_by_provider, "search_results.json", flat=True)  # or flat=False for grouped
        typer.echo("Results written to search_results.json")
    else:
        typer.echo(f"Unsupported export format: {export_format}")
        raise typer.Exit(code=1)

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
    """
    Filters a collection of files based on various criteria such as name, owner, modification/creation dates, and file size.

    Args:
        files (dict): A dictionary where keys are providers and values are lists of file objects.
        name (str, optional): A regex pattern to match file names (case-insensitive).
        owner (str, optional): An email address to match file owners.
        updated_after (str, optional): ISO format datetime string; only include files modified after this date.
        updated_before (str, optional): ISO format datetime string; only include files modified before this date.
        created_after (str, optional): ISO format datetime string; only include files created after this date.
        created_before (str, optional): ISO format datetime string; only include files created before this date.
        min_size (int, optional): Minimum file size in kilobytes (KB).
        max_size (int, optional): Maximum file size in kilobytes (KB).

    Returns:
        list: A list of file objects that match the specified filters.
    """
    def file_matches(file: File):
        if name and not re.search(name, file.name, re.IGNORECASE):
            return False
        if owner and not any(owner in u.email_address for u in file.owners):
            return False
        if updated_after and __parse_dt(file.modified_time) < __parse_dt(updated_after):
            return False
        if updated_before and __parse_dt(file.modified_time) > __parse_dt(updated_before):
            return False
        if created_after and __parse_dt(file.created_time) < __parse_dt(created_after):
            return False
        if created_before and __parse_dt(file.created_time) > __parse_dt(created_before):
            return False
        if min_size and file.size < min_size * 1024:
            return False
        if max_size and file.size > max_size * 1024:
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
    except Exception:
        return val

def __write_csv(files_by_provider, filename):
    # Collect all possible fieldnames from all files
    all_fieldnames = set(["provider"])
    for files in files_by_provider.values():
        for file in files:
            file_dict = file.model_dump() if hasattr(file, 'model_dump') else file.__dict__.copy()
            all_fieldnames.update(file_dict.keys())
    # Move provider to the front, rest sorted
    fieldnames = ["provider"] + sorted(f for f in all_fieldnames if f != "provider")
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for provider, files in files_by_provider.items():
            for file in files:
                file_dict = file.model_dump() if hasattr(file, 'model_dump') else file.__dict__.copy()
                file_dict["provider"] = provider
                # Flatten owners for CSV (only email addresses)
                owners = file_dict.get("owners")
                if isinstance(owners, list):
                    emails = []
                    for u in owners:
                        if hasattr(u, "email_address") and u.email_address:
                            emails.append(u.email_address)
                        elif isinstance(u, dict) and u.get("email_address"):
                            emails.append(u["email_address"])
                        elif isinstance(u, str):
                            emails.append(u)
                    file_dict["owners"] = ";".join(emails)
                # Flatten last_modifying_user for CSV (only email address)
                last_mod = file_dict.get("last_modifying_user")
                if last_mod is not None:
                    if hasattr(last_mod, "email_address"):
                        file_dict["last_modifying_user"] = last_mod.email_address
                    elif isinstance(last_mod, dict) and "email_address" in last_mod:
                        file_dict["last_modifying_user"] = last_mod["email_address"]
                    else:
                        file_dict["last_modifying_user"] = str(last_mod)
                # Flatten parents for CSV
                parents = file_dict.get("parents")
                if isinstance(parents, list):
                    file_dict["parents"] = ";".join(str(p) for p in parents)
                writer.writerow({fn: file_dict.get(fn, "") for fn in fieldnames})

def __write_json(files_by_provider, filename, flat=False):
    with open(filename, "w") as jsonfile:
        if flat:
            all_files = []
            for provider, files in files_by_provider.items():
                for file in files:
                    file_dict = file.model_dump() if hasattr(file, 'model_dump') else file.__dict__.copy()
                    file_dict["provider"] = provider
                    all_files.append(file_dict)
            json.dump(all_files, jsonfile, default=str, indent=2)
        else:
            grouped = {
                provider: [
                    file.model_dump() if hasattr(file, 'model_dump') else file.__dict__.copy()
                    for file in files
                ]
                for provider, files in files_by_provider.items()
            }
            json.dump(grouped, jsonfile, default=str, indent=2)