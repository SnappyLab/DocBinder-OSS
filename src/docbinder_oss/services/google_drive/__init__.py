import logging

from rich.logging import RichHandler

from .google_drive_client import GoogleDriveClient

if not logging.getLogger().handlers:
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

logging.getLogger("googleapiclient").setLevel(logging.WARNING)

def register():
    from .google_drive_client import GoogleDriveClient
    from .google_drive_service_config import GoogleDriveServiceConfig

    # Register the Google Drive client
    return {
        "google_drive": {
            "display_name": "GDrive",
            "config_class": GoogleDriveServiceConfig,
            "client_class": GoogleDriveClient,
        }
    }