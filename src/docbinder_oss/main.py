import typer
from docbinder_oss.cli.provider import app as provider_app
from docbinder_oss.cli.search import app as search_app
from docbinder_oss.cli.setup import app as setup_app

app = typer.Typer()
app.add_typer(provider_app, name="provider")
app.add_typer(search_app)
app.add_typer(setup_app)


# This is the main entry point for the DocBinder CLI.
@app.callback()
def main():
    """DocBinder CLI."""
    pass


if __name__ == "__main__":
    app()
