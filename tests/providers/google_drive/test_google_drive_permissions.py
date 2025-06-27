from docbinder_oss.core.schemas import Permission, User


def test_get_permissions(mock_gdrive_provider, gdrive_client):
    fake_api_response = {
        "permissions": [
            {
                "id": "1234",
                "kind": "drive#permission",
                "type": "user",
                "role": "reader",
                "displayName": "Test User",
                "emailAddress": "test@test.com",
                "photoLink": "https://example.com/photo.jpg",
                "domain": "test.test",
                "deleted": False,
                "expirationTime": None,
            }
        ]
    }
    mock_gdrive_provider.permissions.return_value.list.return_value.execute.return_value = fake_api_response

    permissions = gdrive_client.get_permissions("1234")

    assert isinstance(permissions, list)
    assert len(permissions) == 1
    assert permissions == [
        Permission(
            id="1234",
            kind="drive#permission",
            type="user",
            role="reader",
            user=User(
                display_name="Test User",
                email_address="test@test.com",
                photo_link="https://example.com/photo.jpg",  # type: ignore
                kind="drive#user",
            ),
            domain="test.test",
            deleted=False,
            expiration_time=None,
        )
    ]
