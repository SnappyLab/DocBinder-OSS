from datetime import datetime
import re
import typer
from typing import Optional
import csv
import json

from docbinder_oss.helpers.config import load_config
from docbinder_oss.services import create_provider_instance
from docbinder_oss.helpers.config import Config
from docbinder_oss.services.base_class import BaseProvider
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

    # After collecting all files, build id-to-item mapping for all providers
    all_files = []
    for files in current_files.values():
        all_files.extend(files)

    # Build root_id_to_name mapping for all drives (My Drive, Shared Drives, etc.)
    root_id_to_name = {}
    # Heuristic: a file/folder with no parents or with a special marker is a root
    for f in all_files:
        # If a file has no parents, treat it as a root
        if not getattr(f, 'parents', None) or (isinstance(f.parents, list) and not f.parents[0]):
            root_id_to_name[f.id] = f.name
        # Optionally, if you have a drive_id or drive_name attribute, add here
        # elif hasattr(f, 'drive_id') and hasattr(f, 'drive_name'):
        #     root_id_to_name[f.drive_id] = f.drive_name

    # Fallback for Google Drive: always include 'root': 'My Drive' if not present
    if 'root' not in root_id_to_name:
        root_id_to_name['root'] = 'My Drive'

    id_to_path = build_all_full_paths(all_files, root_id_to_name=root_id_to_name)
    # Add full_path to each file using the memoized paths
    for files in current_files.values():
        for file in files:
            file.full_path = id_to_path.get(file.id, file.name)

    # Filter files per provider, keep grouping
    filtered_files_by_provider = {}
    for provider_name, files in current_files.items():
        filtered = filter_files(
            files,
            name=name,
            owner=owner,
            updated_after=updated_after,
            updated_before=updated_before,
            created_after=created_after,
            created_before=created_before,
            min_size=min_size,
            max_size=max_size,
        )
        filtered_files_by_provider[provider_name] = filtered

    if not export_format:
        typer.echo(filtered_files_by_provider)
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
    results = []
    for file in files:
        if name and not re.search(name, file.name, re.IGNORECASE):
            continue
        if owner and not any(owner in u.email_address for u in file.owners):
            continue
        if updated_after and __parse_dt(file.modified_time) < __parse_dt(updated_after):
            continue
        if updated_before and __parse_dt(file.modified_time) > __parse_dt(updated_before):
            continue
        if created_after and __parse_dt(file.created_time) < __parse_dt(created_after):
            continue
        if created_before and __parse_dt(file.created_time) > __parse_dt(created_before):
            continue
        if min_size and file.size < min_size * 1024:
            continue
        if max_size and file.size > max_size * 1024:
            continue
        results.append(file)
    return results

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