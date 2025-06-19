from typing import Literal

from docbinder_oss.services.base_class import ServiceConfig


class GoogleDriveServiceConfig(ServiceConfig):
    type: Literal["google_drive"] = "google_drive"  # type: ignore[override]
    gcp_credentials_json: str