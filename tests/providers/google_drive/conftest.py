from unittest.mock import MagicMock, patch

import pytest

from docbinder_oss.providers.google_drive.google_drive_client import (
    GoogleDriveClient,
)
from docbinder_oss.providers.google_drive.google_drive_service_config import (
    GoogleDriveServiceConfig,
)


@pytest.fixture
def mock_gdrive_provider():
    """
    This is the core of our testing strategy. We use 'patch' to replace
    the `build` function from the googleapiclient library.

    Whenever `GoogleDriveClient` calls `build('drive', 'v3', ...)`, it will
    receive our mock object instead of making a real network call.
    """
    with patch("docbinder_oss.providers.google_drive.google_drive_client.build") as mock_build:
        # Create a mock for the provider object that `build` would return
        mock_provider = MagicMock()
        # Configure the `build` function to return our mock provider
        mock_build.return_value = mock_provider
        yield mock_provider


@pytest.fixture
def gdrive_client(mock_gdrive_provider):
    """
    Creates an instance of our GoogleDriveClient.
    It will be initialized with a fake config and will use
    the mock_gdrive_provider fixture internally.
    """
    # Patch _get_credentials to avoid real auth
    with patch(
        "docbinder_oss.providers.google_drive.google_drive_client.GoogleDriveClient._get_credentials",
        return_value=MagicMock(),
    ):
        config = GoogleDriveServiceConfig(
            name="test_gdrive",
            gcp_credentials_json="fake_creds.json",
        )
        return GoogleDriveClient(config=config)
