from typing import Optional, List, Any
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from datetime import datetime


class AccessPermission(BaseModel):
    """Represents a permission for a file or folder."""

    user: Optional["User"] = None
    permission: str
    role: str
    expire_at: Optional[datetime] = Field(None, alias="expirationTime")
    
class MetadataResponse(BaseModel):
    """Represents metadata for a file or folder."""

    id: str
    name: str
    mime_type: str = Field(alias="mimeType")
    size: Optional[str] = None  # Size in bytes, as a string
    modified_time: datetime = Field(alias="modifiedTime")
    permissions: List[AccessPermission] = []
    web_link: Optional[HttpUrl] = Field(None, alias="webViewLink")

class User(BaseModel):
    """Represents a ser (e.g., owner, last modifying user, actor)."""

    display_name: Optional[str] = Field(None, alias="displayName")
    email_address: Optional[EmailStr] = Field(None, alias="emailAddress")
    photo_link: Optional[HttpUrl] = Field(None, alias="photoLink")
    kind: Optional[str] = Field(None)


class FileCapabilities(BaseModel):
    """Represents the capabilities of the current user on a file."""

    can_edit: Optional[bool] = Field(None, alias="canEdit")
    can_copy: Optional[bool] = Field(None, alias="canCopy")
    can_share: Optional[bool] = Field(None, alias="canShare")
    can_download: Optional[bool] = Field(None, alias="canDownload")
    can_delete: Optional[bool] = Field(None, alias="canDelete")
    can_rename: Optional[bool] = Field(None, alias="canRename")


class File(BaseModel):
    """Represents a file or folder"""

    id: str
    name: str
    mime_type: str
    kind: Optional[str]

    is_folder: bool = Field(
        False, description="True if the item is a folder, False otherwise."
    )

    web_view_link: Optional[HttpUrl]
    icon_link: Optional[HttpUrl]

    created_time: Optional[datetime]
    modified_time: Optional[datetime]

    owners: Optional[List[User]]
    last_modifying_user: Optional[User]

    size: Optional[str] = Field(
        None, description="Size in bytes, as a string. Only populated for files."
    )
    parents: Optional[List[str]] = Field(None, description="List of parent folder IDs.")

    capabilities: Optional[FileCapabilities] = None

    shared: Optional[bool]
    starred: Optional[bool]
    trashed: Optional[bool]

    # If you want a more robust way to set is_folder after initialization:
    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.mime_type == "application/vnd.google-apps.folder":
            self.is_folder = True
        else:
            self.is_folder = False


class FileList(BaseModel):
    """Represents a paginated list of File items."""

    files: List[File]
    next_page_token: Optional[str]


class Permission(BaseModel):
    """Represents a permission for a file or folder."""

    id: str
    kind: Optional[str]
    type: str
    role: str
    email_address: Optional[EmailStr]
    display_name: Optional[str]
    domain: Optional[str]
    photo_link: Optional[HttpUrl]
    deleted: Optional[bool]
    allow_file_discovery: Optional[bool]


class PermissionList(BaseModel):
    """Represents a list of Permission items."""

    permissions: List[Permission]
    kind: Optional[str] = Field(None)


class Change(BaseModel):
    """Represents a change to an item."""

    user: User = Field(None, alias="user")
    kind: Optional[str] = Field(None)
    change_type: str = Field(alias="changeType")
    time: datetime
    removed: bool
    file_id: Optional[str] = Field(None, alias="fileId")
    file: Optional[File] = Field(
        None, description="The metadata of the changed file, if not removed."
    )
    drive_id: Optional[str] = Field(None, alias="driveId")
    team_drive_id: Optional[str] = Field(None, alias="teamDriveId")


class GDriveChangeList(BaseModel):
    """Represents a paginated list of Change items."""

    changes: List[Change]
    next_page_token: Optional[str] = Field(None, alias="nextPageToken")
    new_start_page_token: Optional[str] = Field(
        None, alias="newStartPageToken"
    )  # Token for the next page of changes
    kind: Optional[str] = Field(None)  # e.g., "drive#changeList"


# Example of how you might structure a Revision model if you go that route for "Recent Activities"
# class GDriveRevision(BaseModel):
#     id: str
#     mime_type: Optional[str] = Field(None, alias='mimeType')
#     kind: Optional[str] = Field(None) # e.g., "drive#revision"
#     modified_time: datetime = Field(alias='modifiedTime')
#     last_modifying_user: Optional[GDriveUser] = Field(None, alias='lastModifyingUser')
#     size: Optional[str] = Field(None)
#     # ... other relevant revision fields

# class GDriveRevisionList(BaseModel):
#     revisions: List[GDriveRevision]
#     kind: Optional[str] = Field(None) # e.g., "drive#revisionList"
#     next_page_token: Optional[str] = Field(None, alias='nextPageToken')
