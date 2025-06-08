from abc import ABC, abstractmethod
from typing import List, Optional
from docbinder_oss.schemas import File, Permission


class BaseStorageClient(ABC):
    """
    Abstract base class for a client that interacts with a cloud storage service.
    Defines a standard interface for listing items and retrieving metadata.
    """

    @abstractmethod
    def list_items(self, folder_id: Optional[str] = None) -> List[File]:
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
    def get_item_metadata(self, item_id: str) -> File:
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
