import typer

app = typer.Typer()


@app.command("get")
def get_provider(
    connection_type: str = typer.Option(None, "--type", "-t", help="The type of the provider to get."),
    name: str = typer.Option(None, "--name", "-n", help="The name of the provider to get."),
):
    """Get connection information for a provider by name or by type.
    If both options are provided, it will search for providers matching either criterion."""
    from docbinder_oss.helpers.config import load_config

    config = load_config()

    provider_found = False
    if not config.providers:
        typer.echo("No providers configured.")
        raise typer.Exit(code=1)
    for provider in config.providers:
        if provider.name == name:
            typer.echo(f"Provider '{name}' found with config: {provider}")
            provider_found = True
        if provider.type == connection_type:
            typer.echo(f"Provider '{provider.name}' of type '{connection_type}'" f" found with config: {provider}")
            provider_found = True
    if not provider_found:
        typer.echo(f"No providers found with name '{name}' or type '{connection_type}'.")
        raise typer.Exit(code=1)
