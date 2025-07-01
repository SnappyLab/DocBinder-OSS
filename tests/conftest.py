from typing import List
from unittest.mock import MagicMock, patch

from pydantic import BaseModel, ConfigDict
import pytest

from docbinder_oss.providers.base_class import BaseProvider
from docbinder_oss.providers.google_drive.google_drive_client import (
    GoogleDriveClient,
)
from docbinder_oss.providers.google_drive.google_drive_service_config import (
    GoogleDriveServiceConfig,
)


class DummyModel(BaseModel):
    id: str
    name: str
    kind: str
    
    model_config = ConfigDict(extra="allow")


class DummyProvider(BaseProvider):
        def __init__(self, name, type=None):
            self.name = name
            self.type = type if type else f"{name}_type"
        
        def list_all_files(self):
            raise NotImplementedError("Please use the pytest parametrize settings to add your test data.")
        def test_connection(self):
            raise NotImplementedError("This provider does not implement connection testing")
        def list_buckets(self):
            raise NotImplementedError("This provider does not implement buckets")
        def get_permissions(self):
            raise NotImplementedError("This provider does not implement permissions")
        def list_files_in_folder(self):
            raise NotImplementedError("This provider does not implement folder listing")
        def get_file_metadata(self, item_id):
            raise NotImplementedError("This provider does not implement file metadata retrieval")

class DummyConfig:
        providers: List[DummyProvider] = []

@pytest.fixture
def sample_data():
    return {
        "provider1": [
            DummyModel(id="1", name="FileA", kind="file"),
            DummyModel(id="2", name="FolderB", kind="folder"),
        ],
        "provider2": [
            DummyModel(id="3", name="FileC", kind="file"),
        ],
    }

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

@pytest.fixture(scope='session')
def load_config_mock(request, create_config_mock):
    """
    This fixture mocks the `load_config` function to return
    a dummy configuration with a specified number of providers.
    """
    name, number_of_providers = request.param
    with patch(
        "docbinder_oss.cli.search.load_config",
        return_value=create_config_mock(name, number_of_providers)
    ) as _fixture:
        yield _fixture

@pytest.fixture(scope='session')
def create_provider_instance_mock(request, create_provider_mock):
    """
    This fixture mocks the `create_provider_instance` function to return
    a dummy provider instance based on the provider name.
    """
    with patch(
        "docbinder_oss.cli.search.create_provider_instance", 
        return_value=create_provider_mock(request.param)
    ) as _fixture:
        yield _fixture

@pytest.fixture(scope="session")
def list_all_files_mock(request):
    """
    
    Yields:
        _type_: _description_
    """
    data = request.param
    with patch("conftest.DummyProvider.list_all_files", return_value=data) as _fixture:
        yield _fixture

@pytest.fixture(scope='session')
def create_provider_mock():
    def create_dummy_provider(name):
        return DummyProvider(name=name, type=f"{name}_type")
    yield create_dummy_provider

@pytest.fixture(scope='session')
def create_config_mock(create_provider_mock):
    """This fixture creates a dummy configuration with a specified number of providers."""
    def create_dummy_config(name, number_of_providers=2):
        dummy_config = DummyConfig()
        dummy_config.providers = [create_provider_mock(f"{name}{i+1}") for i in range(number_of_providers)]
        return dummy_config
    yield create_dummy_config