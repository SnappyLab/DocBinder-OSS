"""
docbinder_oss

A Python library for unified access to storage providers, including Google Drive.

Exports:
    - hello_oss: Example function
    - GoogleDriveClient: Google Drive connector implementing BaseStorageClient
"""

from .main import hello_oss
from .services.google_drive.google_drive_client import GoogleDriveClient
