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

    id: str = Field(repr=True, description="Unique identifier for the file or folder.")
    name: str = Field(repr=True, description="Name of the file or folder. May not be unique.")
    mime_type: str = Field(repr=True, description="MIME type of the file or folder.")
    kind: Optional[str] = Field(repr=True, description="Kind of the item, e.g., 'drive#file'.")

    is_folder: bool = Field(False, description="True if the item is a folder, False otherwise.")

    web_view_link: Optional[HttpUrl]
    icon_link: Optional[HttpUrl]

    created_time: Optional[datetime]
    modified_time: Optional[datetime] = Field(repr=True, description="Last modified time of the file or folder.")

    owners: Optional[List[User]] = Field(repr=True, description="List of owners of the file or folder.")
    last_modifying_user: Optional[User]

    size: Optional[str] = Field(description="Size in bytes, as a string. Only populated for files.")
    parents: Optional[List[str]] = Field(description="Parent folder IDs, if applicable.")

    shared: Optional[bool]
    starred: Optional[bool]
    trashed: Optional[bool]

    def __init__(self, **data: Any):
        # Coerce parents to a list of strings or None
        if "parents" in data:
            if data["parents"] is None:
                data["parents"] = None
            elif isinstance(data["parents"], str):
                data["parents"] = [data["parents"]]
            elif isinstance(data["parents"], list):
                # Ensure all elements are strings
                data["parents"] = [str(p) for p in data["parents"] if p is not None]
            else:
                data["parents"] = [str(data["parents"])]
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
