from datetime import datetime
import os
import pytest
from typer.testing import CliRunner

from docbinder_oss.core.schemas import File
from docbinder_oss.main import app


class DummyFile:
    def __init__(self, id, name, parents=None, is_folder=False):
        self.id = id
        self.name = name
        self.parents = parents or []
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
            DummyFile(id="folder1", name="folder1", parents=["root"], is_folder=True),
            DummyFile(id="file1", name="file1.pdf", parents=["folder1"]),
            DummyFile(id="file2", name="file2.pdf", parents=["folder1"]),
            DummyFile(id="file3", name="file3.pdf", parents=["root"]),
        ]

    class DummyClient:
        def list_all_files(self):
            return list_all_files(self)

    monkeypatch.setattr("docbinder_oss.services.create_provider_instance", lambda cfg: DummyClient())
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(orig_cwd)


def test_list_files(mock_gdrive_service, gdrive_client):
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

    mock_gdrive_service.files.return_value.list.return_value.execute.return_value = (
        fake_api_response
    )

    files = gdrive_client.list_files()

    print(files)

    assert isinstance(files, list)
    assert len(files) == 1
    assert files == [
        File(
            id="1234",
            name="testDrive",
            mime_type="application/vnd.google-apps.drive",
            kind="drive#drive",
            is_folder=False,
            web_view_link="https://drive.google.com/drive/folders/1234",
            icon_link="https://drive.google.com/drive/folders/1234/icon",
            created_time=datetime(2023, 10, 1, 12, 0, 0),
            modified_time=datetime(2023, 10, 1, 12, 0, 0),
            owners=[
                {
                    "display_name": "Test User",
                    "email_address": "test@test.com",
                    "kind": "drive#user",
                    "photo_link": "https://example.com/photo.jpg",
                }
            ],
            last_modifying_user={
                "display_name": "Test User",
                "email_address": "test@test.com",
                "kind": "drive#user",
                "photo_link": "https://example.com/photo.jpg",
            },
            size="1024",
            parents=None,
            shared=True,
            starred=False,
            trashed=False,
        )
    ]


def test_search_finds_all_files_recursively():
    runner = CliRunner()
    result = runner.invoke(app, ["search", "--export-format", "json"])
    assert result.exit_code == 0
    assert os.path.exists("search_results.json")
    import json

    with open("search_results.json") as f:
        data = json.load(f)
        # All files and folders should be included in the results
        file_names = set(d["name"] for d in data)
        expected = {"file1.pdf", "file2.pdf", "file3.pdf", "folder1", "root"}
        assert file_names == expected
        assert len(file_names) == 5
