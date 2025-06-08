from docbinder_oss.services.google_drive_client import GoogleDriveClient

def hello_oss():
    google_drive_client = GoogleDriveClient()
    drives = google_drive_client.list_drives()
    print("Available Drives:")
    print("\n".join(drives))
    for drive in drives:
        print(google_drive_client.get_permissions('18iSGBB9lKbLk855UWrMmQFQhAGmVobDr'))
    return "Hello from docbinder-oss!"

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(hello_oss())