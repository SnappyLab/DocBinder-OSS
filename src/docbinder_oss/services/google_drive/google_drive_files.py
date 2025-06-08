import logging

from googleapiclient.discovery import Resource

from docbinder_oss.core.schemas import File, FileList, User

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = "id,name,mimeType,kind,size,createdTime,modifiedTime,owners(permissionId,displayName,emailAddress,photoLink),lastModifyingUser,webViewLink,iconLink,trashed,shared,starred"


class GoogleDriveFiles:
    def __init__(self, service: Resource):
        self.service = service

    def list_files(self, folder_id=None):
        if len(folder_id.split("|", 1)) > 1:
            logger.warning("Folder ID should not contain '|' character")
            _, folder_id = folder_id.split("|", 1)

        if folder_id == "root":
            query = "'root' in parents and trashed=false"
            resp = (
                self.service.files()
                .list(
                    q=query,
                    fields=f"files({REQUIRED_FIELDS})",
                )
                .execute()
            )
        else:
            resp = (
                self.service.files()
                .list(
                    corpora="drive",
                    q=query or "",
                    driveId=folder_id,
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    fields=f"files({REQUIRED_FIELDS})",
                )
                .execute()
            )

        logger.info(resp.get("files", [])[0])

        logger.info(
            {owner.get("displayName") for owner in resp.get("files")[0].get("owners")}
        )

        return FileList(
            files=[
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
                        email_address=f.get("lastModifyingUser", {}).get(
                            "emailAddress"
                        ),
                        photo_link=f.get("lastModifyingUser", {}).get("photoLink"),
                        kind=f.get("lastModifyingUser", {}).get("kind"),
                    ),
                    web_view_link=f.get("webViewLink"),
                    icon_link=f.get("iconLink"),
                    trashed=f.get("trashed"),
                    shared=f.get("shared"),
                    starred=f.get("starred"),
                    is_folder=f.get("mimeType") == "application/vnd.google-apps.folder",
                    parents=folder_id if folder_id else None,
                )
                for f in resp.get("files")
            ],
            next_page_token=resp.get("nextPageToken"),
        )

    def get_file_metadata(self, file_id: str):
        item_metadata = (
            self.service.files()
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
                display_name=item_metadata.get("lastModifyingUser", {}).get(
                    "displayName"
                ),
                email_address=item_metadata.get("lastModifyingUser", {}).get(
                    "emailAddress"
                ),
                photo_link=item_metadata.get("lastModifyingUser", {}).get("photoLink"),
                kind=item_metadata.get("lastModifyingUser", {}).get("kind"),
            ),
            web_view_link=item_metadata.get("webViewLink"),
            icon_link=item_metadata.get("iconLink"),
            trashed=item_metadata.get("trashed"),
            shared=item_metadata.get("shared"),
            starred=item_metadata.get("starred"),
            is_folder=item_metadata.get("mimeType")
            == "application/vnd.google-apps.folder",
            parents=None,  # This field is not populated by the API, so we set it to None for files.
        )
