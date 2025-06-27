import logging

from googleapiclient.discovery import Resource

from docbinder_oss.core.schemas import Permission, User

logger = logging.getLogger(__name__)


class GoogleDrivePermissions:
    def __init__(self, service: Resource):
        self.service = service

    def get_user(self):
        """
        Retrieves the authenticated user's information.

        Returns:
            User object containing the user's details.
        """
        resp = self.service.about().get(fields="user").execute()  # type: ignore[attr-defined]
        user_info = resp.get("user", {})

        return User(
            display_name=user_info.get("displayName"),
            email_address=user_info.get("emailAddress"),
            photo_link=user_info.get("photoLink"),
            # 'kind' is not always present in the User schema, so we set it to "drive#user"
            #  by default
            kind="drive#user",
        )

    def get_permissions(self, item_id: str):
        resp = self.service.permissions().list(fileId=item_id, fields="permissions").execute()  # type: ignore[attr-defined]

        return [
            Permission(
                id=perm.get("id"),
                kind=perm.get("kind"),
                type=perm.get("type"),
                role=perm.get("role"),
                user=User(
                    display_name=perm.get("displayName"),
                    email_address=perm.get("emailAddress"),
                    photo_link=perm.get("photoLink"),
                    # 'kind' is not always present in the User schema, so we set it to "drive#user"
                    #  by default
                    kind="drive#user",
                ),
                domain=perm.get("domain"),
                deleted=perm.get("deleted"),
                expiration_time=perm.get("expirationTime"),
            )
            for perm in resp.get("permissions")
        ]
