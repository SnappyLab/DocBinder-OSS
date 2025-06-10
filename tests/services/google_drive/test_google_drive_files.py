from datetime import datetime
from docbinder_oss.core.schemas import File


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
            owners=[{"display_name": "Test User", "email_address": "test@test.com", "kind": "drive#user",
                "photo_link": "https://example.com/photo.jpg"}],
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
