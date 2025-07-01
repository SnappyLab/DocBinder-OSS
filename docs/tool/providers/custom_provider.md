# How to Add a New Provider

This guide explains how to integrate a new storage provider (e.g., DropBox, OneDrive) into DocBinder-OSS. The process involves creating configuration and client classes, registering the provider, and ensuring compatibility with the system’s models and interfaces.

---

## 1. Create a Service Configuration Class

Each provider must define a configuration class that inherits from [`ServiceConfig`](https://github.com/SnappyLab/DocBinder-OSS/blob/main/src/docbinder_oss/services/base_class.py):

```python
# filepath: src/docbinder_oss/services/my_provider/my_provider_service_config.py
from docbinder_oss.services.base_class import ServiceConfig

class MyProviderServiceConfig(ServiceConfig):
    type: str = "my_provider"
    name: str
    # Add any other provider-specific fields here
    api_key: str
```

- `type` must be unique and match the provider’s identifier.
- `name` is a user-defined label for this provider instance.

---

## 2. Implement the Storage Client

Create a client class that inherits from [`BaseStorageClient`](https://github.com/SnappyLab/DocBinder-OSS/blob/main/src/docbinder_oss/services/base_class.py) and implements all abstract methods:

```python
# filepath: src/docbinder_oss/services/my_provider/my_provider_client.py
from typing import Optional, List
from docbinder_oss.services.base_class import BaseStorageClient
from docbinder_oss.core.schema import File, Permission
from .my_provider_service_config import MyProviderServiceConfig

class MyProviderClient(BaseStorageClient):
    def __init__(self, config: MyProviderServiceConfig):
        self.config = config
        # Initialize SDK/client here

    def test_connection(self) -> bool:
        # Implement connection test
        pass

    def list_files(self, folder_id: Optional[str] = None) -> List[File]:
        # Implement file listing
        pass

    def get_file_metadata(self, item_id: str) -> File:
        # Implement metadata retrieval
        pass

    def get_permissions(self, item_id: str) -> List[Permission]:
        # Implement permissions retrieval
        pass
```

- Use the shared models [`File`](https://github.com/SnappyLab/DocBinder-OSS/blob/main/src/docbinder_oss/core/schemas.py), [`Permission`](https://github.com/SnappyLab/DocBinder-OSS/blob/main/src/docbinder_oss/core/schemas.py), etc., for return types.

---

## 3. Register the Provider

Add an `__init__.py` in your provider’s folder with a `register()` function:

```python
# filepath: src/docbinder_oss/services/my_provider/__init__.py
from .my_provider_client import MyProviderClient
from .my_provider_service_config import MyProviderServiceConfig

def register():
    return {
        "display_name": "my_provider",
        "config_class": MyProviderServiceConfig,
        "client_class": MyProviderClient,
    }
```

---

## 4. Ensure Discovery

The system will automatically discover your provider if it’s in the `src/docbinder_oss/services/` directory and contains a `register()` function in `__init__.py`.

---

## 5. Update the Config File

Add your provider’s configuration to `~/.config/docbinder/config.yaml`:

```yaml
providers:
  - type: my_provider
    name: my_instance
    # Add other required fields
    api_key: <your-api-key>
```

---

## 6. Test Your Provider

- Run the application and ensure your provider appears and works as expected.
- The config loader will validate your config using your `ServiceConfig` subclass.

---

## Reference

- [src/docbinder_oss/services/base_class.py](https://github.com/SnappyLab/DocBinder-OSS/blob/main/src/docbinder_oss/services/base_class.py)
- [src/docbinder_oss/core/schemas.py](https://github.com/SnappyLab/DocBinder-OSS/blob/main/src/docbinder_oss/core/schemas.py)
- [src/docbinder_oss/services/google_drive/](https://github.com/SnappyLab/DocBinder-OSS/tree/main/src/docbinder_oss/services/google_drive/) (example implementation)
- [src/docbinder_oss/services/__init__.py](https://github.com/SnappyLab/DocBinder-OSS/blob/main/src/docbinder_oss/services/__init__.py)

---

**Tip:** Use the Google Drive as a template for your implementation. Make sure to follow the abstract method signatures and use the shared models for compatibility.