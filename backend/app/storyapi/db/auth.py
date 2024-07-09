from datetime import datetime, timezone

from fastapi_utils.api_model import APIModel
from pydantic import Field, field_validator

from common.services.cypher import Cypher
from storyapi.config.settings import settings


class BearerToken(APIModel):
    """The token has always an expiration,
     which is returned by expires_at field.
     The token has access to all merchants assigned to your app."""

    token_type: str = Field(default='Bearer', alias='token_type')
    expires_at: datetime = Field(..., alias='expires_at')  # with TZ "2019-07-16T11:20:26.221Z"
    access_token: str = Field(default='Bearer', alias='access_token')

    @field_validator("expires_at")
    def convert_expires_at(cls, v):
        # convert to UTC time zone after reading from DB
        if isinstance(v, datetime) and v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
            return v
        return v


class AuthSQL(BearerToken):
    client_id: str = Field(default=settings.story_api_client_id, alias='client_id')
    secret: str = Field(default=settings.story_api_client_secret, alias='secret')
    client_name: str = Field(default="The Miners Borislavka s.r.o.", alias='client_name')

    @field_validator("secret", mode='before')
    def check_secret_decrypt(cls, p, values):

        if p and isinstance(p, bytes):
            p = Cypher().decrypt(p)

        return p
