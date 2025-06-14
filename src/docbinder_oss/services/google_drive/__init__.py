import logging

from rich.logging import RichHandler

from .google_drive_client import GoogleDriveClient

if not logging.getLogger().handlers:
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

logging.getLogger("googleapiclient").setLevel(logging.WARNING)
