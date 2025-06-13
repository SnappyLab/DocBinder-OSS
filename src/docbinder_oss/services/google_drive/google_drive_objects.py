import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class GoogleDriveObjects:
    def __init__(self, service: Any):
        self.service = service

    def list_objects(self, bucket_name: str) -> List[str]:
        _, bucket_id = bucket_name.split('|', 1)
        try:
            if bucket_id == 'root':
                query = "'root' in parents and trashed=false"
                resp = self.service.files().list(q=query, fields="files(id,name)").execute()
            else:
                resp = self.service.files().list(
                    corpora='drive',
                    driveId=bucket_id,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    fields="files(id,name)"
                ).execute()
            return [f"{f['name']}|{f['id']}" for f in resp.get('files', [])]
        except Exception as e:
            logger.error(f"Error listing objects: {e}")
            return []

    def get_object_metadata(self, object_name: str) -> Dict:
        _, obj_id = object_name.split('|', 1)
        try:
            resp = self.service.files().get(
                fileId=obj_id,
                fields='id,name,mimeType,size,modifiedTime,owners/displayName,owners/emailAddress,lastModifyingUser,permissions,webViewLink'
            ).execute()
            return {
                'id': resp.get('id'),
                'name': resp.get('name'),
                'mimeType': resp.get('mimeType'),
                'size': resp.get('size', 'und'),
                'modifiedTime': resp.get('modifiedTime'),
                'owners_name': resp.get('owners', [{}])[0].get('displayName'),
                'owners_email': resp.get('owners', [{}])[0].get('emailAddress'),
                'web_link': resp.get('webViewLink'),
            }
        except Exception as e:
            logger.error(f"Error getting object metadata: {e}")
            return {}

    def get_objects_metadata(self, object_name_list: List[str]): # type: to add
        # This method can be further improved to fetch only requested files
        try:
            bucket_id = 'root'  # Default to root for now
            if bucket_id == 'root':
                query = "'root' in parents and trashed=false"
                resp = self.service.files().list(q=query, fields="files(id,name,mimeType,size,modifiedTime,owners(permissionId,displayName,emailAddress),lastModifyingUser,permissions(displayName,type,role,emailAddress),webViewLink)").execute()
            else:
                resp = self.service.files().list(
                    corpora='drive',
                    driveId=bucket_id,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    fields="files(id,name,mimeType,size,modifiedTime,owners(permissionId,displayName,emailAddress,photoLink),lastModifyingUser,permissions(id,displayName,type,role,emailAddress,photoLink,expirationTime),webViewLink)"
                ).execute()
            files = resp.get('files', [])
            if not files:
                logger.warning("No files found for the provided object names")
                return []
            logger.info(f"Retrieved metadata for {len(files)} files")
            return [
                MetadataResponse(
                    id=metadata_document.get('id'),
                    name=metadata_document.get('name'),
                    mimeType=metadata_document.get('mimeType'),
                    size=metadata_document.get('size', 'und'),
                    modifiedTime=metadata_document.get('modifiedTime'),
                    permissions=[
                        AccessPermission(
                            user=User(
                                id=perm.get('id', 'und'),
                                name=perm.get('displayName', 'und'),
                                email=perm.get('emailAddress', 'und'),
                                avatarUrl=perm.get('photoLink', 'und')
                            ),
                            permission=perm.get('type'),
                            role=perm.get('role'),
                            expireAt=perm.get('expirationTime')
                        ) for perm in metadata_document.get('permissions', [])
                    ],
                    web_link=metadata_document.get('webViewLink'),
                ) for metadata_document in files
            ]
        except Exception as e:
            logger.error(f"Error getting objects metadata: {e}")
            return []
