def register():
    from .dropbox_client import DropboxClient
    from .dropbox_service_config import DropboxServiceConfig

    # Register the Google Drive client
    return {
        "google_drive": {
            "display_name": "Dropbox",
            "config_class": DropboxServiceConfig,
            "client_class": DropboxClient,
        }
    }