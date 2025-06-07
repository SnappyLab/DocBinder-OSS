import logging
from googleapiclient.discovery import Resource
from typing import List

logger = logging.getLogger(__name__)

class GoogleDriveBuckets:
    def __init__(self, service: Resource):
        self.service = service

    def list_buckets(self) -> List[str]:
        drives = [{'id': 'root', 'name': 'My Drive'}]
        try:
            resp = self.service.drives().list().execute()
            for d in resp.get('drives', []):
                drives.append({'id': d['id'], 'name': d['name']})
        except Exception as e:
            logger.error(f"Error listing buckets: {e}")
        return [f"{d['name']}|{d['id']}" for d in drives]
