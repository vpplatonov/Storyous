from datetime import datetime

from fastapi_utils.api_model import APIModel
from pydantic import Field

from common.db.mssql import RepositoryMSSQL
from storyapi.config.settings import settings


class BearerToken(APIModel):
    """The token has always an expiration,
     which is returned by expires_at field.
     The token has access to all merchants assigned to your app."""

    token_type: str = Field(default='Bearer', alias='token_type')
    expires_at: datetime = Field(..., alias='expires_at')  # "2019-07-16T11:20:26.221Z"
    access_token: str = Field(default='Bearer', alias='access_token')


class AuthSQL(BearerToken):
    client_id: str = Field(default=settings.story_api_client_id, alias='client_id')
    secret: str = Field(default=settings.story_api_client_secret, alias='secret')
    client_name: str = Field(default="The Miners Borislavka s.r.o.", alias='client_name')


class ClientsAndAuthRepositorySQL(RepositoryMSSQL[AuthSQL]):
    primary_key = "client_id"
    pk_remove_on_create = False
