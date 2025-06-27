import typer

app = typer.Typer()


@app.command()
def list():
    """List all configured providers."""
    from docbinder_oss.helpers.config import load_config

    config = load_config()
    if not config.providers:
        typer.echo("No providers configured.")
        raise typer.Exit(code=1)

    for provider in config.providers:
        typer.echo(f"Provider: {provider.name}, type: {provider.type}")
