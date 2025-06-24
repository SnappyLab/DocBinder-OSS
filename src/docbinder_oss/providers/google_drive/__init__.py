import logging

from rich.logging import RichHandler

from .google_drive_client import GoogleDriveClient
from .google_drive_service_config import GoogleDriveServiceConfig

if not logging.getLogger().handlers:
    FORMAT = "%(message)s"
    logging.basicConfig(level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

logging.getLogger("googleapiclient").setLevel(logging.WARNING)


def register() -> dict:
    """
    Register the Google Drive service provider.
    """

    # Register the Google Drive client
    return {
        "display_name": "google_drive",
        "config_class": GoogleDriveServiceConfig,
        "client_class": GoogleDriveClient,
    }


def get_service_name() -> str:
    """
    Returns the name of the service.
    This is used for logging and identification purposes.
    """
    return "Google Drive"


def get_service_display_name() -> str:
    """
    Returns the display name of the service.
    This is used for user-friendly identification.
    """
    return "Google Drive Service"
