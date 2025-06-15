import typer
from docbinder_oss.helpers.config import save_config, validate_config

app = typer.Typer()

from docbinder_oss.commands import search
from docbinder_oss.commands import setup
from docbinder_oss.commands.provider import list, get, test


# This is the main entry point for the DocBinder CLI.
@app.callback()
def main():
    """DocBinder CLI."""
    pass


@app.command()
def hello():
    """Print a friendly greeting."""
    typer.echo("Hello, DocBinder OSS!")

if __name__ == "__main__":
    app()
