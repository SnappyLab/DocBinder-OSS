import logging

from googleapiclient.discovery import Resource

from docbinder_oss.core.schemas import Permission, PermissionList, User

logger = logging.getLogger(__name__)


class GoogleDrivePermissions:
    def __init__(self, service: Resource):
        self.service = service

    def get_permissions(self, item_id: str):
        resp = (
            self.service.permissions()
            .list(fileId=item_id, fields="permissions")
            .execute()
        )

        return PermissionList(
            permissions=[
                Permission(
                    id=perm.get("id"),
                    kind=perm.get("kind"),
                    type=perm.get("type"),
                    role=perm.get("role"),
                    user=User(
                        display_name=perm.get("displayName"),
                        email_address=perm.get("emailAddress"),
                        photo_link=perm.get("photoLink"),
                        kind="drive#user",  # 'kind' is not always present in the User schema, so we set it to "drive#user" by default
                    ),
                    domain=perm.get("domain"),
                    deleted=perm.get("deleted"),
                    expiration_time=perm.get("expirationTime"),
                )
                for perm in resp.get("permissions")
            ],
        )
