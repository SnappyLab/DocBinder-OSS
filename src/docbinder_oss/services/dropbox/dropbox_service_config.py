from typing import Final, Literal

from docbinder_oss.services.base_class import ServiceConfig


class DropboxServiceConfig(ServiceConfig):
    type: Literal["dropbox"] = "dropbox"  # type: ignore[override]
    api_key: str
