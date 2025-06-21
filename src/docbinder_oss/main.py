from typing import Annotated, List, Optional

import typer
import yaml

from docbinder_oss.helpers.config import save_config, validate_config
from docbinder_oss.services import create_provider_instance

app = typer.Typer()

# --- Provider Subcommand Group ---
# We create a separate Typer app for the 'provider' command.
# This allows us to nest commands like 'provider list' and 'provider get'.
provider_app = typer.Typer(
    help="Commands to manage providers. List them or get details for a specific one."
)
# We add this group to our main application.
app.add_typer(provider_app, name="provider")


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


@provider_app.command()
def list():
    """List all configured providers."""
    from docbinder_oss.helpers.config import load_config

    config = load_config()
    if not config.providers:
        typer.echo("No providers configured.")
        raise typer.Exit(code=1)

    for provider in config.providers:
        typer.echo(f"Provider: {provider.name}, Type: {provider.type}")


@provider_app.command("get")
def get_provider(
    connection_type: str = typer.Option(
        None, "--type", "-t", help="The type of the provider to get."
    ),
    name: str = typer.Option(
        None, "--name", "-n", help="The name of the provider to get."
    ),
):
    """Get connection information for a specific provider."""
    from docbinder_oss.helpers.config import load_config

    config = load_config()

    count = 0
    if not config.providers:
        typer.echo("No providers configured.")
        raise typer.Exit(code=1)
    for provider in config.providers:
        if provider.name == name:
            typer.echo(f"Provider '{name}' found with config: {provider}")
            count += 1
        if provider.type == connection_type:
            typer.echo(
                f"Provider '{provider.name}' of type "
                f"'{connection_type}' found with config: {provider}"
            )
            count += 1
    if count == 0:
        typer.echo(
            f"No providers found with name '{name}' or type '{connection_type}'."
        )
        raise typer.Exit(code=1)


@provider_app.command("test")
def test(
    name: Annotated[
        str, typer.Argument(help="The name of the provider to test the connection.")
    ],
):
    """Test the connection to a specific provider."""
    from docbinder_oss.helpers.config import load_config

    config = load_config()
    if not config.providers:
        typer.echo("No providers configured.")
        raise typer.Exit(code=1)
    for provider_config in config.providers:
        if provider_config.name == name:
            typer.echo(f"Testing connection for provider '{name}'...")
            try:
                client = create_provider_instance(provider_config)
                client.test_connection()
                typer.echo(f"Connection to provider '{name}' is successful.")
            except Exception as e:
                typer.echo(f"Failed to connect to provider '{name}': {e}")
            return
    # If we reach here, the provider was not found
    typer.echo(f"Provider '{name}' not found in configuration.")
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
