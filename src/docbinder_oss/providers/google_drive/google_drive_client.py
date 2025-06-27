import logging
import os
from typing import List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from docbinder_oss.core.schemas import Bucket, File, Permission
from docbinder_oss.providers.base_class import BaseProvider
from docbinder_oss.providers.google_drive.google_drive_buckets import GoogleDriveBuckets
from docbinder_oss.providers.google_drive.google_drive_files import GoogleDriveFiles
from docbinder_oss.providers.google_drive.google_drive_permissions import (
    GoogleDrivePermissions,
)
from docbinder_oss.providers.google_drive.google_drive_service_config import (
    GoogleDriveServiceConfig,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GoogleDriveClient(BaseProvider):
    def __init__(self, config: GoogleDriveServiceConfig):
        super().__init__(config)
        logger.info("Initializing Google Drive client")
        self.SCOPES = [
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
            "https://www.googleapis.com/auth/drive.activity.readonly",
        ]
        self.settings = config
        self.creds = self._get_credentials()
        self.service = build("drive", "v3", credentials=self.creds)
        self.buckets = GoogleDriveBuckets(self.service)
        self.files = GoogleDriveFiles(self.service)
        self.permissions = GoogleDrivePermissions(self.service)

    def _get_credentials(self):
        logger.info("Getting credentials for Google Drive client")

        TOKEN_PATH = os.path.expanduser("~/.config/docbinder/gcp/" + self.config.name + "_token.json")
        # Ensure the directory exists
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        logger.debug(f"Token path: {TOKEN_PATH}")

        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, scopes=self.SCOPES)
        except (FileNotFoundError, ValueError):
            logger.warning("Credentials file not found or invalid, re-authenticating")
            creds = None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.settings.gcp_credentials_json, self.SCOPES)
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

    def list_buckets(self) -> list[Bucket]:
        return self.buckets.list_buckets()

    def list_files_in_folder(self, folder_id: Optional[str] = None) -> List[File]:
        return self.files.list_files_in_folder(folder_id)

    def list_all_files(self) -> List[File]:
        return self.files.list_files_in_folder()

    def get_file_metadata(self, item_id: str) -> File:
        return self.files.get_file_metadata(item_id)

    def get_permissions(self, file_id: str) -> List[Permission]:
        return self.permissions.get_permissions(file_id)
