def register():
    from .google_drive_client import GoogleDriveClient
    from .google_drive_service_config import GoogleDriveServiceConfig

    # Register the Google Drive client
    return {
        "google_drive": {
            "display_name": "GDrive",
            "config_class": GoogleDriveServiceConfig,
            "client_class": GoogleDriveClient,
        }
    }