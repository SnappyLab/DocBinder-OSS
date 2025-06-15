from docbinder_oss.commands.provider import provider_app
import typer

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