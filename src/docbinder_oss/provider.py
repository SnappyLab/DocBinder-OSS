from typing import Annotated
import typer
from .main import app
from docbinder_oss.services import create_provider_instance


# --- Provider Subcommand Group ---
# We create a separate Typer app for the 'provider' command.
# This allows us to nest commands like 'provider list' and 'provider get'.
provider_app = typer.Typer(
    help="Commands to manage providers. List them or get details for a specific one."
)
# We add this group to our main application.
app.add_typer(provider_app, name="provider")

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
                f"Provider '{provider.name}' of type '{connection_type}' found with config: {provider}"
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
                if client is None:
                    typer.echo(f"Provider '{name}' is not supported or not implemented.")
                    raise typer.Exit(code=1)
                # Attempt to test the connection
                client.test_connection()
                typer.echo(f"Connection to provider '{name}' is successful.")
            except Exception as e:
                typer.echo(f"Failed to connect to provider '{name}': {e}")
            return
    # If we reach here, the provider was not found
    typer.echo(f"Provider '{name}' not found in configuration.")
    raise typer.Exit(code=1)
