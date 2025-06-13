import os
from typing import Annotated, List, Union

from pydantic import BaseModel, Field, ValidationError
import typer
import yaml

from docbinder_oss.services.dropbox.dropbox_service_config import DropboxProviderConfig
from docbinder_oss.services.google_drive.google_drive_service_config import GoogleProviderConfig

CONFIG_PATH = os.path.expanduser("~/.config/docbinder/config.yaml")

ProviderConfig = Annotated[
    Union[GoogleProviderConfig, DropboxProviderConfig],
    Field(discriminator="type")
]

class ConfigSchema(BaseModel):
    providers: List[ProviderConfig]


def load_config() -> ConfigSchema:
    if not os.path.exists(CONFIG_PATH):
        typer.echo(f"Config file not found at {CONFIG_PATH}. Please run 'docbinder setup' first.")
        raise typer.Exit(code=1)
    with open(CONFIG_PATH, "r") as f:
        config_data = yaml.safe_load(f)
    try:
        return ConfigSchema(**config_data)
    except ValidationError as e:
        typer.echo(f"Config file validation error:\n{e}")
        raise typer.Exit(code=1)
    

def save_config(config: ConfigSchema):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False)
    typer.echo(f"Config saved to {CONFIG_PATH}")

def validate_config(config_data: dict) -> ConfigSchema:
    """Validate configuration data using Pydantic."""
    if not config_data:
        typer.echo("No configuration data provided.")
        raise typer.Exit(code=1)
    try:
        return ConfigSchema(**config_data)
    except ValidationError as e:
        typer.echo(f"Provider config validation error:\n{e}")
        raise typer.Exit(code=1)