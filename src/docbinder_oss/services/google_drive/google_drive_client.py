import logging
from typing import Optional, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
<<<<<<< HEAD

from docbinder_oss.core.config import settings
from docbinder_oss.core.schemas import Bucket, File, Permission
from docbinder_oss.services.base_client import BaseStorageClient
from docbinder_oss.services.google_drive.google_drive_buckets import GoogleDriveBuckets
from docbinder_oss.services.google_drive.google_drive_files import GoogleDriveFiles
from docbinder_oss.services.google_drive.google_drive_permissions import (
    GoogleDrivePermissions,
)
=======
from ..base_client import BaseStorageClient
from .google_drive_buckets import GoogleDriveBuckets
from .google_drive_objects import GoogleDriveObjects
from .google_drive_permissions import GoogleDrivePermissions
>>>>>>> 860d13c335fecb7e3d8058d97858d1229efcbbb2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GoogleDriveClient(BaseStorageClient):
    def __init__(self, credentials: Optional[Credentials] = None):
        logger.info("Initializing Google Drive client")
        self.SCOPES = [
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
            "https://www.googleapis.com/auth/drive.activity.readonly",
        ]
        self.creds = credentials or self._get_credentials()
        self.service = build("drive", "v3", credentials=self.creds)
        self.buckets = GoogleDriveBuckets(self.service)
        self.files = GoogleDriveFiles(self.service)
        self.permissions = GoogleDrivePermissions(self.service)

    def _get_credentials(self):
        try:
            creds = Credentials.from_authorized_user_file(
                settings.gcp_token_json, scopes=self.SCOPES
            )
        except (FileNotFoundError, ValueError):
            logger.warning("Credentials file not found or invalid, re-authenticating")
            creds = None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.gcp_credentials_json, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("gcp_token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    def list_buckets(self) -> List[Bucket]:
        return self.buckets.list_buckets()

    def list_files(self, folder_id: Optional[str] = None) -> List[File]:
        return self.files.list_files(folder_id)

    def get_file_metadata(self, file_id: str) -> File:
        return self.files.get_file_metadata(file_id)

    def get_permissions(self, file_id: str) -> List[Permission]:
        return self.permissions.get_permissions(file_id)
