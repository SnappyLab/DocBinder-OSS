from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel

from docbinder_oss.core.schemas import File, Permission


class ServiceConfig(BaseModel):
    """Abstract base class for configuration settings."""

    type: str
    name: str


class BaseStorageClient(ABC):
    """
    Abstract base class for a client that interacts with a cloud storage service.
    Defines a standard interface for listing items and retrieving metadata.
    """

    def __init__(self, config: ServiceConfig):
        self.name = config.name
        self.config = config

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Tests the connection to the storage service.

        Returns:
            True if the connection is successful, False otherwise.
        """
        pass

    @abstractmethod
    def list_files(self, folder_id: Optional[str] = None) -> List[File]:
        """
        Lists items (files and folders) within a specific folder.

        Args:
            folder_id: The unique ID of the folder to list. If None,
                       lists items in the root directory.

        Returns:
            A list of StorageItem objects representing the files and folders.
        """
        pass

    @abstractmethod
    def get_file_metadata(self, item_id: str) -> File:
        """
        Retrieves all available metadata for a specific file or folder.

        Args:
            item_id: The unique ID of the file or folder.

        Returns:
            A StorageItem object with detailed metadata.
        """
        pass

    @abstractmethod
    def get_permissions(self, item_id: str) -> List[Permission]:
        """
        Retrieves the access control list for a specific file or folder.

        Args:
            item_id: The unique ID of the file or folder.

        Returns:
            A list of Permission objects, each detailing a principal's
            access role.
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"
