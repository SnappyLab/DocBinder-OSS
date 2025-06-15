from typing import List, Optional

import typer
import yaml

from docbinder_oss.helpers.config import save_config, validate_config

app = typer.Typer()


# This is the main entry point for the DocBinder CLI.
@app.callback()
def main():
    """DocBinder CLI."""
    pass


@app.command()
def hello():
    """Print a friendly greeting."""
    typer.echo("Hello, DocBinder OSS!")


@app.command()
def setup(
    file: Optional[str] = typer.Option(None, "--file", help="Path to YAML config file"),
    provider: Optional[List[str]] = typer.Option(
        None,
        "--provider",
        help="Provider config as provider:key1=val1,key2=val2",
        callback=lambda v: v or [],
    ),
):
    """Setup DocBinder configuration via YAML file or provider key-value pairs."""
    config_data = {}
    if file:
        with open(file, "r") as f:
            config_data = yaml.safe_load(f) or {}
    elif provider:
        providers = {}
        for entry in provider:
            if ":" not in entry:
                typer.echo(
                    f"Provider entry '{entry}' must be in provider:key1=val1,key2=val2 format."
                )
                raise typer.Exit(code=1)
            prov_name, prov_kvs = entry.split(":", 1)
            kv_dict = {}
            for pair in prov_kvs.split(","):
                if "=" not in pair:
                    typer.echo(f"Provider config '{pair}' must be in key=value format.")
                    raise typer.Exit(code=1)
                k, v = pair.split("=", 1)
                kv_dict[k] = v
            providers[prov_name] = kv_dict
        config_data["providers"] = providers
    validated = validate_config(config_data)
    if not validated.providers:
        typer.echo("No providers configured. Please add at least one provider.")
        raise typer.Exit(code=1)
    # Save the validated config
    try:
        save_config(validated)
    except Exception as e:
        typer.echo(f"Error saving config: {e}")
        raise typer.Exit(code=1)
    typer.echo("Configuration saved successfully.")

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
    export_format: str = typer.Option("csv", "--export-format", help="Export format: csv or json", show_default=True),
):
    """Search for files or folders matching filters across all providers and export results as CSV or JSON."""
    import re
    import csv
    import json
    from datetime import datetime
    from docbinder_oss.helpers.config import load_config
    from docbinder_oss.services import create_provider_instance

    config = load_config()
    if not config.providers:
        typer.echo("No providers configured.")
        raise typer.Exit(code=1)

    results = []
    for provider_config in config.providers:
        if provider and provider_config.name != provider:
            continue
        client = create_provider_instance(provider_config)
        if client is None or not hasattr(client, "list_all_files"):
            continue
        try:
            files = client.list_all_files()
            for item in files:
                # Name regex filter
                if name:
                    if not re.search(name, item.name or "", re.IGNORECASE):
                        continue
                # Owner/contributor/reader email filter
                if owner:
                    emails = set()
                    owners_list = getattr(item, "owners", None) or []
                    emails.update([u.email_address for u in owners_list if u and getattr(u, "email_address", None)])
                    last_mod_user = getattr(item, "last_modifying_user", None)
                    if last_mod_user and getattr(last_mod_user, "email_address", None):
                        emails.add(last_mod_user.email_address)
                    if owner not in emails:
                        continue
                # Last update filter
                if updated_after:
                    if not item.modified_time or datetime.fromisoformat(str(item.modified_time)) < datetime.fromisoformat(updated_after):
                        continue
                if updated_before:
                    if not item.modified_time or datetime.fromisoformat(str(item.modified_time)) > datetime.fromisoformat(updated_before):
                        continue
                # Created at filter
                if created_after:
                    if not item.created_time or datetime.fromisoformat(str(item.created_time)) < datetime.fromisoformat(created_after):
                        continue
                if created_before:
                    if not item.created_time or datetime.fromisoformat(str(item.created_time)) > datetime.fromisoformat(created_before):
                        continue
                # Size filter (in KB)
                if min_size is not None:
                    try:
                        if not item.size or int(item.size) < min_size * 1024:
                            continue
                    except Exception:
                        continue
                if max_size is not None:
                    try:
                        if not item.size or int(item.size) > max_size * 1024:
                            continue
                    except Exception:
                        continue
                # Collect all possible params for export
                results.append({
                    "provider": provider_config.name,
                    "id": getattr(item, "id", None),
                    "name": getattr(item, "name", None),
                    "size": getattr(item, "size", None),
                    "mime_type": getattr(item, "mime_type", None),
                    "created_time": getattr(item, "created_time", None),
                    "modified_time": getattr(item, "modified_time", None),
                    "owners": ",".join([u.email_address for u in (getattr(item, "owners", None) or []) if u and getattr(u, "email_address", None)]) if getattr(item, "owners", None) else None,
                    "last_modifying_user": getattr(getattr(item, "last_modifying_user", None), "email_address", None),
                    "web_view_link": getattr(item, "web_view_link", None),
                    "web_content_link": getattr(item, "web_content_link", None),
                    "shared": getattr(item, "shared", None),
                    "trashed": getattr(item, "trashed", None),
                })
        except Exception as e:
            typer.echo(f"Error searching provider '{provider_config.name}': {e}")
    # Write results to CSV or JSON
    if results:
        fieldnames = [
            "provider", "id", "name", "size", "mime_type", "created_time", "modified_time", "owners", "last_modifying_user", "web_view_link", "web_content_link", "shared", "trashed"
        ]
        if export_format.lower() == "json":
            with open("search_results.json", "w") as jsonfile:
                json.dump(results, jsonfile, indent=2, default=str)
            typer.echo(f"{len(results)} results written to search_results.json")
        else:
            with open("search_results.csv", "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in results:
                    writer.writerow(row)
            typer.echo(f"{len(results)} results written to search_results.csv")
    else:
        typer.echo("No results found.")
    return results

if __name__ == "__main__":
    app()
