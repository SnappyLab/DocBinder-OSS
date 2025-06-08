from docbinder_oss.services.google_drive.google_drive_client import GoogleDriveClient


def hello_oss():
    google_drive_client = GoogleDriveClient()
    drives = google_drive_client.get_file_metadata(
        "19QYV33CQLL0bHjr12-Fud4EMv-NEsqnxh52-bi72CM8"
    )
    logger.info(f"{drives}")
    return "Hello from docbinder-oss!"


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(hello_oss())
