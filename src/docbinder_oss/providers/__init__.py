import importlib
import logging
import pkgutil
from pathlib import Path
from typing import Annotated, Optional, Union

from pydantic import Field
from rich.logging import RichHandler

from docbinder_oss import providers
from docbinder_oss.providers.base_class import BaseProvider, ServiceConfig

if not logging.getLogger().handlers:
    FORMAT = "%(message)s"
    logging.basicConfig(level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

logging.getLogger("services").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

_provider_registry = None  # Module-level cache


def get_provider_registry() -> dict:
    """
    Returns the provider registry containing all registered service providers.
    Uses a module-level cache to avoid repeated dynamic imports.
    """
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = {}
        for _, name, _ in pkgutil.iter_modules(__path__):
            if name not in ("base_class", "__init__"):
                module = importlib.import_module(f".{name}", __package__)
                if hasattr(module, "register"):
                    provider_info = module.register()
                    _provider_registry[name] = {**provider_info}
    return _provider_registry


def create_provider_instance(config: ServiceConfig) -> Optional["BaseProvider"]:
    """
    Factory function to create a provider instance from its config.
    """
    registry = get_provider_registry()
    entry = registry.get(config.type)
    if not entry:
        logger.warning(f"Unknown provider type '{config.type}'. Skipping.")
        return None
    return entry["client_class"](config)


def load_services(package):
    """
    Dynamically imports all modules in a package.
    This is the key to the "plug-and-play" system.
    """
    package_path = Path(package.__file__).parent
    logger.info(f"--- Discovering services in: {package_path} ---")

    # pkgutil.iter_modules is a robust way to find all modules in a package
    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        if module_name == "base_class" or module_name == "__init__":
            # Skip the base_class and __init__ modules
            continue
        # Construct the full module path
        full_module_path = f"{package.__name__}.{module_name}"
        try:
            # Import the module
            importlib.import_module(full_module_path)
            logger.info(f"Successfully imported service module: {full_module_path}")
        except Exception as e:
            logger.error(f"Failed to import {full_module_path}. Error: {e}")


def get_service_union() -> Annotated:
    """
    Dynamically creates a discriminated union of all ServiceConfig subclasses.
    """
    subclasses = ServiceConfig.__subclasses__()
    if not subclasses:
        raise TypeError(
            "No subclasses of ServiceConfig found. "
            "The automatic service loader might have failed or the services directory is empty."
        )
    dynamic_union = Union[*subclasses]
    return Annotated[dynamic_union, Field(discriminator="type")]


load_services(providers)
ServiceUnion = get_service_union()
