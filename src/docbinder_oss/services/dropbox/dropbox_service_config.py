from typing import Literal
from pydantic import BaseModel


class DropboxServiceConfig(BaseModel):
    type: Literal["dropbox"]
    api_key: str
