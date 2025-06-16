import logging

from rich.logging import RichHandler

from .onedrive_client import OneDriveClient
from .onedrive_service_config import OneDriveServiceConfig

if not logging.getLogger().handlers:
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

logging.getLogger("onedriveclient").setLevel(logging.WARNING)


def register() -> dict:
    """
    Register the OneDrive service provider.
    """

    # Register the OneDrive client
    return {
        "display_name": "onedrive",
        "config_class": OneDriveServiceConfig,
        "client_class": OneDriveClient,
    }
