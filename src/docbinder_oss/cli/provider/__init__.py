import typer
from .get import app as get_app
from .list import app as list_app
from .test import app as test_app

# --- Provider Subcommand Group ---
# We create a separate Typer app for the 'provider' command.
# This allows us to nest commands like 'provider list' and 'provider get'.
app = typer.Typer(help="Commands to manage providers. List them or get details for a specific one.")
app.add_typer(get_app)
app.add_typer(list_app)
app.add_typer(test_app)
