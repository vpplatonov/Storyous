from typing import Optional

from common.config.settings import (
    settings as common_settings,
    Settings as BaseSettings
)


class Settings(BaseSettings):
    story_api_url: Optional[str]
    story_api_login: Optional[str]
    story_api_client_id: Optional[str]
    story_api_client_secret: Optional[str]
    story_api_merchant_id: Optional[str]


settings = Settings()
