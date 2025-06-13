from typing import Literal, Optional
from pydantic import BaseModel

class GoogleDriveServiceConfig(BaseModel):
    type: Literal["google"]
    gcp_credentials_json: str
    gcp_token_json: str
    optional_setting_example: Optional[str] = None