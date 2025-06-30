import logging

from googleapiclient.discovery import Resource

from docbinder_oss.core.schemas import File, User

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = (
    "id,name,mimeType,kind,size,createdTime,modifiedTime,"
    "owners(permissionId,displayName,emailAddress,photoLink),"
    "lastModifyingUser(permissionId,displayName,emailAddress,photoLink),"
    "webViewLink,iconLink,trashed,shared,starred,parents"
)


class GoogleDriveFiles:
    def __init__(self, service: Resource):
        self.service = service

    def list_files_in_folder(self, bucket_id: str | None = None) -> list[File]:
        args = {
            "fields": f"nextPageToken,files({REQUIRED_FIELDS})",
            "pageSize": 1000,
        }

        if bucket_id:
            args["q"] = f"'{bucket_id}' in parents and trashed=false"
        else:
            args["q"] = "trashed=false"

        resp = self.service.files().list(**args).execute()
        files = resp.get("files", [])
        next_page_token = resp.get("nextPageToken")

        while next_page_token:
            logger.debug("Getting next page...")
            current_page = self.service.files().list(**args, pageToken=next_page_token).execute()
            files.extend(current_page.get("files", []))
            next_page_token = current_page.get("nextPageToken")

        return [
            File(
                id=f.get("id"),
                name=f.get("name"),
                kind=f.get("kind"),
                mime_type=f.get("mimeType"),
                size=f.get("size"),
                created_time=f.get("createdTime", None),
                modified_time=f.get("modifiedTime", None),
                owners=[
                    User(
                        display_name=owner.get("displayName"),
                        email_address=owner.get("emailAddress"),
                        photo_link=owner.get("photoLink"),
                        kind=owner.get("kind"),
                    )
                    for owner in f.get("owners")
                ],
                last_modifying_user=User(
                    display_name=f.get("lastModifyingUser", {}).get("displayName"),
                    email_address=f.get("lastModifyingUser", {}).get("emailAddress"),
                    photo_link=f.get("lastModifyingUser", {}).get("photoLink"),
                    kind=f.get("lastModifyingUser", {}).get("kind"),
                ),
                web_view_link=f.get("webViewLink"),
                icon_link=f.get("iconLink"),
                trashed=f.get("trashed"),
                shared=f.get("shared"),
                starred=f.get("starred"),
                is_folder=f.get("mimeType") == "application/vnd.google-apps.folder",
                parents=f.get("parents") if isinstance(f.get("parents"), list) else None,
            )
            for f in files
        ]

    def get_file_metadata(self, file_id: str):
        item_metadata = (
            self.service.files()  # type: ignore[attr-defined]
            .get(
                fileId=file_id,
                fields=f"{REQUIRED_FIELDS}",
            )
            .execute()
        )

        return File(
            id=item_metadata.get("id"),
            name=item_metadata.get("name"),
            kind=item_metadata.get("kind"),
            mime_type=item_metadata.get("mimeType"),
            size=item_metadata.get("size"),
            created_time=item_metadata.get("createdTime", None),
            modified_time=item_metadata.get("modifiedTime", None),
            owners=[
                User(
                    display_name=owner.get("displayName"),
                    email_address=owner.get("emailAddress"),
                    photo_link=owner.get("photoLink"),
                    kind=owner.get("kind"),
                )
                for owner in item_metadata.get("owners")
            ],
            last_modifying_user=User(
                display_name=item_metadata.get("lastModifyingUser", {}).get("displayName"),
                email_address=item_metadata.get("lastModifyingUser", {}).get("emailAddress"),
                photo_link=item_metadata.get("lastModifyingUser", {}).get("photoLink"),
                kind=item_metadata.get("lastModifyingUser", {}).get("kind"),
            ),
            web_view_link=item_metadata.get("webViewLink"),
            icon_link=item_metadata.get("iconLink"),
            trashed=item_metadata.get("trashed"),
            shared=item_metadata.get("shared"),
            starred=item_metadata.get("starred"),
            is_folder=item_metadata.get("mimeType") == "application/vnd.google-apps.folder",
            parents=None,  # This field is not populated by the API, so we set it to None for files.
        )
