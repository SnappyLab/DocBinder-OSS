import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from docbinder_oss.services.base_client import BaseStorageClient
from docbinder_oss.services.google_drive.google_drive_buckets import GoogleDriveBuckets
from docbinder_oss.services.google_drive.google_drive_objects import GoogleDriveObjects
from docbinder_oss.services.google_drive.google_drive_permissions import GoogleDrivePermissions
from docbinder_oss.helpers.config import load_config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class GoogleDriveClient(BaseStorageClient):
    def __init__(self):
        logger.info("Initializing Google Drive client")
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/drive.activity.readonly'
        ]
        self.config = load_config()
        if not self.config.providers or 'google' not in self.config.providers:
            logger.error("Google provider configuration not found")
            raise ValueError("Google provider configuration is required. Run 'docbinder setup' to configure it.")
        self.settings = self.config.providers['google']
        self.creds = self._get_credentials()
        self.service = build('drive', 'v3', credentials=self.creds)
        self.buckets = GoogleDriveBuckets(self.service)
        self.objects = GoogleDriveObjects(self.service)
        self.permissions = GoogleDrivePermissions(self.service)

    def _get_credentials(self):
        try:
            creds = Credentials.from_authorized_user_file(
                self.settings.gcp_token_json,
                scopes=self.SCOPES
            )
        except (FileNotFoundError, ValueError):
            logger.warning("Credentials file not found or invalid, re-authenticating")
            creds = None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.settings.gcp_credentials_json, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("gcp_token.json", "w") as token:
                token.write(creds.to_json())
        return creds
    
    def get_user_info(self) -> dict:
        """Retrieve user information from Google Drive."""
        try:
            about = self.service.about().get(fields='user').execute()
            return about.get('user', {})
        except Exception as e:
            logger.error(f"Failed to retrieve user info: {e}")
            return {}

    def list_buckets(self) -> list[str]:
        return self.buckets.list_buckets()

    def list_objects(self, bucket_name: str) -> list[str]:
        return self.objects.list_objects(bucket_name)

    def get_object_metadata(self, object_name: str) -> dict:
        return self.objects.get_object_metadata(object_name)

    def list_access(self, bucket_name: str) -> dict:
        return self.permissions.list_access(bucket_name)

    def list_permissions(self, bucket_name: str, object_name: str) -> dict:
        return self.permissions.list_permissions(bucket_name, object_name)