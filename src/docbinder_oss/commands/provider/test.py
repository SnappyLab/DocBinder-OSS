from docbinder_oss.commands.provider import provider_app
import typer
from typing import Annotated
from docbinder_oss.services import create_provider_instance

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