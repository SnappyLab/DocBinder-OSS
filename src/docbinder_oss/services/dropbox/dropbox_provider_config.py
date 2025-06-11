from typing import Literal
from pydantic import BaseModel


class DropboxProviderConfig(BaseModel):
    type: Literal["dropbox"]
    api_key: str
