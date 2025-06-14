from typing import Literal

from docbinder_oss.services.base_class import ServiceConfig


class DropboxServiceConfig(ServiceConfig):
    type: Literal["dropbox"] = "dropbox"
    api_key: str
