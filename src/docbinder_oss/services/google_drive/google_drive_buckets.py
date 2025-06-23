import logging
from typing import List

from googleapiclient.discovery import Resource

from docbinder_oss.core.schemas import Bucket

logger = logging.getLogger(__name__)


class GoogleDriveBuckets:
    def __init__(self, service: Resource):
        self.service = service

    def list_buckets(self) -> List[Bucket]:
        drives = [
            Bucket(
                id="root",
                name="My Drive",
                kind="drive#drive",
                created_time=None,
                viewable=True,
                restrictions=None,
            )
        ]  # Default root drive

        resp = (
            self.service.drives()  # type: ignore[attr-defined]
            .list(fields="drives(id,name,kind,createdTime,hidden,restrictions)")
            .execute()
        )

        for drive in resp.get("drives", []):
            drives.append(
                Bucket(
                    id=drive.get("id"),
                    name=drive.get("name"),
                    kind=drive.get("kind", "drive#drive"),
                    created_time=drive.get("createdTime"),
                    viewable=not drive.get("hidden"),
                    restrictions=drive.get("restrictions"),
                )
            )

        return drives
