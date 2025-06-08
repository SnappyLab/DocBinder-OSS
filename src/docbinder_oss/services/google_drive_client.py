import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from docbinder_oss.schemas import AccessPermission, File, FileList, Permission, PermissionList, User
from docbinder_oss.services.base_client import BaseStorageClient
from docbinder_oss.core.config import settings

logger = logging.getLogger(__name__)


class GoogleDriveClient(BaseStorageClient):
    def __init__(self):
        logger.info("Initializing Google Drive client")
        SCOPES = [
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
            "https://www.googleapis.com/auth/drive.activity.readonly",
        ]
        try:
            creds = Credentials.from_authorized_user_file(
                settings.gcp_token_json, scopes=SCOPES
            )
        except (FileNotFoundError, ValueError):
            logger.warning("Credentials file not found or invalid, re-authenticating")
            creds = None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.gcp_credentials_json, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("gcp_token.json", "w") as token:
                token.write(creds.to_json())
        self.service = build("drive", "v3", credentials=creds)
        
    def list_drives(self) -> list[str]:
        drives = []
        # "My Drive" root
        drives.append({"id": "root", "name": "My Drive"})
        resp = self.service.drives().list().execute()
        for d in resp.get("drives", []):
            drives.append({"id": d["id"], "name": d["name"]})
        # return as "name|id" tokens
        return [f"{d['name']}|{d['id']}" for d in drives]

    def list_items(self, folder_id = None):
        if len(folder_id.split("|", 1)) > 1:
            logger.warning("Folder ID should not contain '|' character")
            _, folder_id = folder_id.split("|", 1)
        
        if folder_id == "root":
            query = "'root' in parents and trashed=false"
            resp = (
                self.service.files()
                .list(
                    q=query,
                    fields="files(id,name,mimeType,size,modifiedTime,owners(permissionId,displayName,emailAddress),lastModifyingUser,permissions(displayName,type,role,emailAddress),webViewLink)",
                )
                .execute()
            )
        else:
            resp = (
                self.service.files()
                .list(
                    corpora="drive",
                    q=query or "",
                    driveId=folder_id,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    fields="files(id,name,mimeType,size,createdTime,modifiedTime,owners(permissionId,displayName,emailAddress,photoLink),lastModifyingUser,permissions(id,displayName,type,role,emailAddress,photoLink,expirationTime),webViewLink)",
                )
                .execute()
            )
            
        return FileList(
            files=[
                File(
                    id=f.get("id"),
                    name=f.get("name"),
                    mimeType=f.get("mimeType"),
                    size=f.get("size", "und"),
                    createdTime=f.get("createdTime", None),
                    modifiedTime=f.get("modifiedTime", None),
                    owners=[
                        User(
                            id=owner.get("permissionId", "und"),
                            name=owner.get("displayName", "und"),
                            email=owner.get("emailAddress", "und"),
                            avatarUrl=owner.get("photoLink", "und"),
                        )
                        for owner in f.get("owners", [])
                    ],
                    lastModifyingUser=User(
                        id=f.get("lastModifyingUser", {}).get("permissionId", "und"),
                        name=f.get("lastModifyingUser", {}).get("displayName", "und"),
                        email=f.get("lastModifyingUser", {}).get("emailAddress", "und"),
                    ),
                    permissions=[
                        AccessPermission(
                            user=User(
                                id=perm.get("id", "und"),
                                name=perm.get("displayName", "und"),
                                email=perm.get("emailAddress", "und"),
                                avatarUrl=perm.get("photoLink", "und"),
                            ),
                            permission=perm.get("type"),
                            role=perm.get("role"),
                            expireAt=perm.get("expirationTime"),
                        )
                        for perm in f.get("permissions", [])
                    ],
                    web_view_link=f.get("webViewLink"),
                    is_folder=f.get("mimeType") == "application/vnd.google-apps.folder"
                )
                for f in resp.get("files", [])
            ],
            next_page_token=resp.get("nextPageToken")
        )
    
    def get_item_metadata(self, item_id: str):
        item_metadata = self.service.files().get(
            fileId=item_id,
            fields="id,name,mimeType,size,createdTime,modifiedTime,owners(permissionId,displayName,emailAddress,photoLink),lastModifyingUser,permissions(id,displayName,type,role,emailAddress,photoLink,expirationTime),webViewLink"
        ).execute()
        
        return File(
                    id=item_metadata.get("id"),
                    name=item_metadata.get("name"),
                    mimeType=item_metadata.get("mimeType"),
                    size=item_metadata.get("size", "und"),
                    createdTime=item_metadata.get("createdTime", None),
                    modifiedTime=item_metadata.get("modifiedTime", None),
                    owners=[
                        User(
                            id=owner.get("permissionId", "und"),
                            name=owner.get("displayName", "und"),
                            email=owner.get("emailAddress", "und"),
                            avatarUrl=owner.get("photoLink", "und"),
                        )
                        for owner in item_metadata.get("owners", [])
                    ],
                    lastModifyingUser=User(
                        id=item_metadata.get("lastModifyingUser", {}).get("permissionId", "und"),
                        name=item_metadata.get("lastModifyingUser", {}).get("displayName", "und"),
                        email=item_metadata.get("lastModifyingUser", {}).get("emailAddress", "und"),
                    ),
                    permissions=[
                        AccessPermission(
                            user=User(
                                id=perm.get("id", "und"),
                                name=perm.get("displayName", "und"),
                                email=perm.get("emailAddress", "und"),
                                avatarUrl=perm.get("photoLink", "und"),
                            ),
                            permission=perm.get("type"),
                            role=perm.get("role"),
                            expireAt=perm.get("expirationTime"),
                        )
                        for perm in item_metadata.get("permissions", [])
                    ],
                    web_view_link=item_metadata.get("webViewLink"),
                    is_folder=item_metadata.get("mimeType") == "application/vnd.google-apps.folder"
                )
    
    def get_permissions(self, item_id: str):
        resp = (
            self.service.permissions()
            .list(fileId=item_id, fields="permissions")
            .execute()
        )
        
        return PermissionList(
            permissions=[
                Permission(
                    id=perm.get("id"),
                    kind=perm.get("kind"),
                    type=perm.get("type"),
                    role=perm.get("role"),
                    email_address=perm.get("emailAddress"),
                    display_name=perm.get("displayName"),
                    domain=perm.get("domain"),
                    photo_link=perm.get("photoLink"),
                    deleted=perm.get("deleted", False),
                    allow_file_discovery=perm.get("allowFileDiscovery", False)
                )
            for perm in resp.get("permissions", [])
            ],
        )
