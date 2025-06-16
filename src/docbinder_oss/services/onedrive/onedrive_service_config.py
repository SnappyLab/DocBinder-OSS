from typing import Literal

from docbinder_oss.services.base_class import ServiceConfig


class OneDriveServiceConfig(ServiceConfig):
    type: Literal["onedrive"] = "onedrive"  # type: ignore[override]
    tenant_id: str
    client_id: str
    client_secret: str
    refresh_token: str
