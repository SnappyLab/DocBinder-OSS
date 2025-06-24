import logging

from googleapiclient.discovery import Resource

from docbinder_oss.core.schemas import Bucket, File, User

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

    def list_files_in_folder(self, bucket_id: str | None = None, is_drive_root: bool = False) -> list[File]:
        args = {
            "includeItemsFromAllDrives": True,
            "supportsAllDrives": True,
            "fields": f"nextPageToken,files({REQUIRED_FIELDS})",
        }
        if bucket_id is None:
            logger.debug("Listing files in the root directory.")
            bucket_id = "root"
        else:
            logger.debug(f"{type(bucket_id)}: {bucket_id}")

        if is_drive_root and bucket_id != "root":
            args.update(
                {
                    "corpora": "drive",
                    "driveId": bucket_id,
                    "q": "'root' in parents and trashed=false",
                }
            )
        else:
            parent_id = bucket_id
            if parent_id == "root" or parent_id is None:
                args["q"] = "'root' in parents and trashed=false"
            else:
                args["q"] = f"'{parent_id}' in parents and trashed=false"  
        
        resp = self.service.files().list(**args).execute()
        print(len(resp["files"]))
        # exit(1)
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
            for f in resp.get("files")
        ]

    def list_files_recursively(self, bucket: str) -> list[File]:
        """List all files in the Google Drive bucket, including all subfolders."""
        is_drive_root = bucket != "root"

        def _recursive_list(folder_id: str):
            logger.debug(f"Listing files in folder: {folder_id}")
            items: list[File] = self.list_files_in_folder(folder_id, is_drive_root=is_drive_root)
            all_items = []
            for item in items:
                all_items.append(item)
                # Recursively list files in subfolders
                if hasattr(item, "is_folder") and item.is_folder:
                    all_items.extend(_recursive_list(item.id))
            return all_items

        return _recursive_list(bucket)

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

    def list_all_files(self, buckets: list[Bucket]) -> list[File]:
        files = []
        for bucket in buckets:
            files.extend(self.list_files_recursively(bucket.id))
        return files
