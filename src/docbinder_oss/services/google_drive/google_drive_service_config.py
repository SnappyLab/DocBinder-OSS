from typing import Literal, Optional

from docbinder_oss.services.base_class import ServiceConfig


class GoogleDriveServiceConfig(ServiceConfig):
    type: Literal["google_drive"] = "google_drive"
    gcp_credentials_json: str
    gcp_token_json: str
    optional_setting_example: Optional[str] = None
