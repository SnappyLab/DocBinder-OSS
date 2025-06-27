from datetime import datetime
import os
import pytest


class DummyFile:
    def __init__(self, id, name, parents=None, is_folder=False):
        self.id = id
        self.name = name
        # Always use a list for parents, or None
        if parents is None:
            self.parents = None
        elif isinstance(parents, list):
            self.parents = parents
        else:
            self.parents = [parents]
        self.is_folder = is_folder
        self.size = 1000
        # Use correct mime_type for folders and files
        self.mime_type = "application/vnd.google-apps.folder" if is_folder else "application/pdf"
        self.created_time = "2024-01-01T00:00:00"
        self.modified_time = "2024-01-02T00:00:00"
        self.owners = [type("User", (), {"email_address": "owner@example.com"})()]
        self.last_modifying_user = type("User", (), {"email_address": "mod@example.com"})()
        self.web_view_link = "http://example.com/view"
        self.web_content_link = "http://example.com/content"
        self.shared = True
        self.trashed = False


@pytest.fixture(autouse=True)
def patch_provider(monkeypatch, tmp_path):
    class DummyProviderConfig:
        name = "googledrive"

    class DummyConfig:
        providers = [DummyProviderConfig()]

    monkeypatch.setattr("docbinder_oss.helpers.config.load_config", lambda: DummyConfig())

    # Simulate a folder structure: root -> folder1 -> file1, file2; root -> file3
    def list_all_files(self):
        return [
            DummyFile(id="root", name="root", is_folder=True),
            DummyFile(id="folder1", name="folder1", parents="root", is_folder=True),
            DummyFile(id="file1", name="file1.pdf", parents="folder1"),
            DummyFile(id="file2", name="file2.pdf", parents="folder1"),
            DummyFile(id="file3", name="file3.pdf", parents="root"),
        ]

    class DummyClient:
        def list_all_files(self):
            return list_all_files(self)

    monkeypatch.setattr("docbinder_oss.providers.create_provider_instance", lambda cfg: DummyClient())
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(orig_cwd)


def test_list_files(mock_gdrive_provider, gdrive_client):
    fake_api_response = {
        "files": [
            {
                "id": "1234",
                "name": "testDrive",
                "mimeType": "application/vnd.google-apps.drive",
                "kind": "drive#drive",
                "isFolder": False,
                "webViewLink": "https://drive.google.com/drive/folders/1234",
                "iconLink": "https://drive.google.com/drive/folders/1234/icon",
                "createdTime": datetime(2023, 10, 1, 12, 0, 0),
                "modifiedTime": datetime(2023, 10, 1, 12, 0, 0),
                "owners": [
                    {
                        "displayName": "Test User",
                        "emailAddress": "test@test.com",
                        "photoLink": "https://example.com/photo.jpg",
                        "kind": "drive#user",
                    }
                ],
                "lastModifyingUser": {
                    "displayName": "Test User",
                    "emailAddress": "test@test.com",
                    "photoLink": "https://example.com/photo.jpg",
                    "kind": "drive#user",
                },
                "size": "1024",
                "parents": "root",
                "shared": True,
                "starred": False,
                "trashed": False,
            },
        ]
    }

    mock_gdrive_provider.files.return_value.list.return_value.execute.return_value = fake_api_response

    files = gdrive_client.list_files_in_folder()

    print(files)

    assert isinstance(files, list)
    assert len(files) == 1
    # Compare fields individually to match the actual File model structure
    file = files[0]
    assert file.id == "1234"
    assert file.name == "testDrive"
    assert file.mime_type == "application/vnd.google-apps.drive"
    assert file.kind == "drive#drive"
    assert file.is_folder is False
    assert str(file.web_view_link) == "https://drive.google.com/drive/folders/1234"
    assert str(file.icon_link) == "https://drive.google.com/drive/folders/1234/icon"
    assert file.created_time == datetime(2023, 10, 1, 12, 0, 0)
    assert file.modified_time == datetime(2023, 10, 1, 12, 0, 0)
    assert len(file.owners) == 1
    owner = file.owners[0]
    assert getattr(owner, "display_name", None) == "Test User"
    assert getattr(owner, "email_address", None) == "test@test.com"
    assert getattr(owner, "kind", None) == "drive#user"
    assert str(getattr(owner, "photo_link", "")) == "https://example.com/photo.jpg"
    last_mod = file.last_modifying_user
    assert getattr(last_mod, "display_name", None) == "Test User"
    assert getattr(last_mod, "email_address", None) == "test@test.com"
    assert getattr(last_mod, "kind", None) == "drive#user"
    assert str(getattr(last_mod, "photo_link", "")) == "https://example.com/photo.jpg"
    assert file.size == "1024"
    # Accept None or any list value for parents
    assert file.parents is None or isinstance(file.parents, list)
    assert file.shared is True
    assert file.starred is False
    assert file.trashed is False
