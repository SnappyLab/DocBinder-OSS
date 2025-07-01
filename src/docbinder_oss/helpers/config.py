import logging
from pathlib import Path  
from typing import List
import typer
import yaml
from pydantic import BaseModel, ValidationError

from docbinder_oss.providers import ServiceUnion, get_provider_registry

logger = logging.getLogger(__name__)

CONFIG_PATH = Path("~/.config/docbinder/config.yaml").expanduser()

class Config(BaseModel):
    """Main configuration model that holds a list of all provider configs."""
    providers: List[ServiceUnion] # type: ignore


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        typer.echo(
            f"Config file not found at {CONFIG_PATH}. Please run 'docbinder setup' first."
        )
        raise typer.Exit(code=1)

    with open(CONFIG_PATH, "r") as f:
        config_data = yaml.safe_load(f)

    provider_registry = get_provider_registry()
    config_to_add = []
    for config in config_data.get("providers", []):
        if config.get("type") not in provider_registry:
            typer.echo(f"Unknown provider type: {config['type']}")
            raise typer.Exit(code=1)
        config_to_add.append(provider_registry[config["type"]]["config_class"](**config))
    try:
        configss = Config(providers=config_to_add)
        return configss
    except ValidationError as e:
        typer.echo(f"Config file validation error:\n{e}")
        raise typer.Exit(code=1)


def save_config(config: Config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False)
    typer.echo(f"Config saved to {CONFIG_PATH}")


def validate_config(config_data: dict) -> Config:
    """Validate configuration data using Pydantic."""
    if not config_data:
        typer.echo("No configuration data provided.")
        raise typer.Exit(code=1)
    try:
        config = Config.model_validate(config_data)
        return config
    except ValidationError as e:
        typer.echo(f"Provider config validation error:\n{e}")
        raise typer.Exit(code=1)
