from unittest.mock import MagicMock, patch

import pytest

from docbinder_oss.services.google_drive.google_drive_client import (
    GoogleDriveClient,
)


@pytest.fixture
def mock_gdrive_service():
    """
    This is the core of our testing strategy. We use 'patch' to replace
    the `build` function from the googleapiclient library.

    Whenever `GoogleDriveClient` calls `build('drive', 'v3', ...)`, it will
    receive our mock object instead of making a real network call.
    """
    with patch(
        "docbinder_oss.services.google_drive.google_drive_client.build"
    ) as mock_build:
        # Create a mock for the service object that `build` would return
        mock_service = MagicMock()
        # Configure the `build` function to return our mock service
        mock_build.return_value = mock_service
        yield mock_service


@pytest.fixture
def gdrive_client(mock_gdrive_service):
    """
    Creates an instance of our GoogleDriveClient.
    It will be initialized with a fake credentials object and will use
    the mock_gdrive_service fixture internally.
    """
    # We can use a simple MagicMock for credentials as we are not testing the auth part.
    mock_creds = MagicMock()
    return GoogleDriveClient(credentials=mock_creds)
