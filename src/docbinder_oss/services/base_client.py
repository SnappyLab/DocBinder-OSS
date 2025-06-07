from abc import ABC, abstractmethod

class BaseStorageClient(ABC):
    @abstractmethod
    def list_buckets(self) -> list[str]:
        pass

    @abstractmethod
    def list_objects(self, bucket_name: str) -> list[str]:
        pass

    @abstractmethod
    def get_object_metadata(self, bucket_name: str, object_name: str) -> dict:
        pass

    @abstractmethod
    def list_access(self, bucket_name: str) -> dict:
        """Return mapping of principals to permissions"""
        pass
    
    @abstractmethod
    def list_permissions(self, bucket_name: str, object_name: str) -> dict:
        """Return mapping of principals to permissions"""
        pass