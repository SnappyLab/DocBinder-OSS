import typer
from docbinder_oss.main import app

# --- Provider Subcommand Group ---
# We create a separate Typer app for the 'provider' command.
# This allows us to nest commands like 'provider list' and 'provider get'.
provider_app = typer.Typer(
    help="Commands to manage providers. List them or get details for a specific one."
)
# We add this group to our main application.
app.add_typer(provider_app, name="provider")
