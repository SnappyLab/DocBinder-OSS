import typer
from typing import Annotated

app = typer.Typer()


@app.command("test")
def test(
    name: Annotated[str, typer.Argument(help="The name of the provider to test the connection.")],
):
    """Test the connection to a specific provider."""
    from docbinder_oss.helpers.config import load_config
    from docbinder_oss.providers import create_provider_instance

    if not name:
        typer.echo("Provider name is required.")
        raise typer.Exit(code=1)

    config = load_config()
    if not config.providers:
        typer.echo("No providers configured.")
        raise typer.Exit(code=1)

    found_provider_config = None
    for provider_config in config.providers:
        if provider_config.name == name:
            found_provider_config = provider_config
            break  # Exit the loop once the provider is found

    if found_provider_config:
        typer.echo(f"Testing connection for provider '{name}'...")
        try:
            client = create_provider_instance(found_provider_config)
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
