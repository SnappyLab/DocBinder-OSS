from datetime import datetime

from docbinder_oss.core.schemas import Bucket


def test_list_buckets(mock_gdrive_provider, gdrive_client):
    fake_api_response = {
        "drives": [
            {
                "id": "1234",
                "name": "testDrive",
                "kind": "drive#drive",
                "createdTime": datetime(2023, 10, 1, 12, 0, 0),
                "hidden": False,
                "restrictions": {
                    "adminManagedRestrictions": True,
                    "copyRequiresWriterPermission": False,
                    "domainUsersOnly": True,
                    "driveMembersOnly": False,
                },
            }
        ]
    }
    mock_gdrive_provider.drives.return_value.list.return_value.execute.return_value = fake_api_response

    buckets = gdrive_client.list_buckets()

    assert isinstance(buckets, list)
    assert len(buckets) == 2
    assert buckets == [
        Bucket(
            id="root",
            name="My Drive",
            kind="drive#drive",
            created_time=None,
            viewable=True,
            restrictions=None,
        ),
        Bucket(
            id="1234",
            name="testDrive",
            kind="drive#drive",
            created_time=datetime(2023, 10, 1, 12, 0),
            viewable=True,
            restrictions={
                "adminManagedRestrictions": True,
                "copyRequiresWriterPermission": False,
                "domainUsersOnly": True,
                "driveMembersOnly": False,
            },
        ),
    ]
