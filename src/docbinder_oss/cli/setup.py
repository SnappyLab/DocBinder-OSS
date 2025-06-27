import typer
from typing import List, Optional
import yaml
from docbinder_oss.helpers.config import save_config, validate_config

app = typer.Typer(help="DocBinder configuration setup commands.")


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
                typer.echo(f"Provider entry '{entry}' must be in provider:key1=val1,key2=val2 format.")
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
