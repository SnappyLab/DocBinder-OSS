from typing import Literal

from docbinder_oss.providers.base_class import ServiceConfig


class GoogleDriveServiceConfig(ServiceConfig):
    type: Literal["google_drive"] = "google_drive"  # type: ignore[override]
    name: str
    gcp_credentials_json: str
