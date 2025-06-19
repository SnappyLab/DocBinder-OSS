import logging
import os
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from docbinder_oss.core.schemas import File, Permission, User
from docbinder_oss.services.base_class import BaseStorageClient
from docbinder_oss.services.google_drive.google_drive_buckets import GoogleDriveBuckets
from docbinder_oss.services.google_drive.google_drive_files import GoogleDriveFiles
from docbinder_oss.services.google_drive.google_drive_permissions import (
    GoogleDrivePermissions,
)
from docbinder_oss.services.google_drive.google_drive_service_config import (
    GoogleDriveServiceConfig,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GoogleDriveClient(BaseStorageClient):
    def __init__(self, config: GoogleDriveServiceConfig):
        super().__init__(config)
        logger.info("Initializing Google Drive client")
        self.SCOPES = [
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
            "https://www.googleapis.com/auth/drive.activity.readonly",
        ]
        self.config = config
        self.creds = self._get_credentials()
        self.service = build("drive", "v3", credentials=self.creds)
        self.buckets = GoogleDriveBuckets(self.service)
        self.files = GoogleDriveFiles(self.service)
        self.permissions = GoogleDrivePermissions(self.service)

    def _get_credentials(self):
        TOKEN_PATH = os.path.expanduser("~/.config/docbinder/gcp/" + self.config.name + "_token.json")
        # Ensure the directory exists
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)

        try:
            creds = Credentials.from_authorized_user_file(
                TOKEN_PATH, scopes=self.SCOPES
            )
        except (FileNotFoundError, ValueError):
            logger.warning("Credentials file not found or invalid, re-authenticating")
            creds = None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.gcp_credentials_json, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
        return creds

    def test_connection(self) -> bool:
        try:
            self.permissions.get_user()
            return True
        except Exception as e:
            logger.error(f"Test connection failed: {e}")
            return False

    def list_buckets(self) -> list:
        return self.buckets.list_buckets()

    def list_files(self, folder_id: Optional[str] = None) -> List[File]:
        return self.files.list_files(folder_id)
    
    def list_all_files(self) -> List[File]:
        """
        Recursively list all files and folders in all buckets (drives).
        Handles My Drive and Shared Drives correctly.
        """
        def _recursive_list(folder_id, is_drive_root=False):
            items = self.files.list_files(folder_id, is_drive_root=is_drive_root)
            all_items = []
            for item in items:
                all_items.append(item)
                # Use mime_type to check if this is a folder
                if getattr(item, "mime_type", None) == "application/vnd.google-apps.folder":
                    all_items.extend(_recursive_list(item.id))
            return all_items

        buckets = self.list_buckets()
        all_files = []
        for bucket in buckets:
            # If bucket.id == "root", it's My Drive; otherwise, it's a shared drive
            is_drive_root = bucket.id != "root"
            all_files.extend(_recursive_list(bucket.id, is_drive_root=is_drive_root))
        return all_files

    def get_file_metadata(self, item_id: str) -> File:
        return self.files.get_file_metadata(item_id)

    def get_permissions(self, item_id: str) -> List[Permission]:
        return self.permissions.get_permissions(item_id)
    