import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GoogleDrivePermissions:
    def __init__(self, service: Any):
        self.service = service
    def list_access(self, bucket_name: str) -> Dict:
        _, bucket_id = bucket_name.split('|', 1)
        try:
            resp = self.service.permissions().list(
                fileId=bucket_id,
                fields='permissions(id,type,role,emailAddress,domain)'
            ).execute()
            access = {}
            for perm in resp.get('permissions', []):
                grantee = perm.get('emailAddress') or perm.get('domain') or perm.get('id')
                access.setdefault(grantee, []).append(perm.get('role'))
            return access
        except Exception as e:
            logger.error(f"Error listing access: {e}")
            return {}

    def list_permissions(self, bucket_name: str, object_name: str) -> Dict:
        _, obj_id = object_name.split('|', 1)
        try:
            resp = self.service.permissions().list(
                fileId=obj_id,
                fields='permissions'
            ).execute()
            permissions = {}
            for perm in resp.get('permissions', []):
                grantee = perm.get('emailAddress') or perm.get('domain') or perm.get('id')
                permissions.setdefault(grantee, []).append(perm.get('role'))
            return permissions
        except Exception as e:
            logger.error(f"Error listing permissions: {e}")
            return {}
