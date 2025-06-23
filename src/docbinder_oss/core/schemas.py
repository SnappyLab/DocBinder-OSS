from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class Bucket(BaseModel):
    """
    Represents a bucket in the document system.
    A bucket is a top-level container for files and folders.
    """

    id: str
    name: str
    kind: Optional[str] = Field(description="Type of the bucket, e.g., 'drive#file'")
    created_time: Optional[datetime] = Field(description="Timestamp when the bucket was created.")
    viewable: Optional[bool]
    restrictions: Optional[Dict[str, Any]]


class User(BaseModel):
    """Represents a user (e.g., owner, last modifying user, actor)."""

    display_name: Optional[str]
    email_address: Optional[EmailStr]
    photo_link: Optional[HttpUrl]
    kind: Optional[str]


class FileCapabilities(BaseModel):
    """Represents the capabilities of the current user on a file."""

    can_edit: Optional[bool]
    can_copy: Optional[bool]
    can_share: Optional[bool]
    can_download: Optional[bool]
    can_delete: Optional[bool]
    can_rename: Optional[bool]


class File(BaseModel):
    """Represents a file or folder"""

    id: str
    name: str
    mime_type: str
    kind: Optional[str]

    is_folder: bool = Field(False, description="True if the item is a folder, False otherwise.")

    web_view_link: Optional[HttpUrl]
    icon_link: Optional[HttpUrl]

    created_time: Optional[datetime]
    modified_time: Optional[datetime]

    owners: Optional[List[User]]
    last_modifying_user: Optional[User]

    size: Optional[str] = Field(description="Size in bytes, as a string. Only populated for files.")
    parents: Optional[str] = Field(description="Parent folder ID, if applicable.")

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


class Permission(BaseModel):
    """Represents a permission for a file or folder."""

    id: str
    kind: Optional[str]
    type: str
    role: str
    user: User
    domain: Optional[str]
    deleted: Optional[bool]
    expiration_time: Optional[str]
