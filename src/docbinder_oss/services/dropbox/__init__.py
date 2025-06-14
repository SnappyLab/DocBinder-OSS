from .dropbox_client import DropboxClient
from .dropbox_service_config import DropboxServiceConfig


def register():
    # Register the Dropbox client
    return {
        "display_name": "dropbox",
        "config_class": DropboxServiceConfig,
        "client_class": DropboxClient,
    }
