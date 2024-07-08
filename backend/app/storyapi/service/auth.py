import functools
import time
from datetime import datetime, timezone
from typing import Generic, get_args

import pydantic
import requests

from common.config import T
from storyapi.config import param_to_str
from storyapi.config.settings import settings
from storyapi.db.auth import BearerToken, ClientsAndAuthRepositorySQL, AuthSQL


class BearerService:
    # Header
    headers: dict = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    # Body: must be merged by & sign
    payload: dict = {
        "client_id": settings.story_api_client_id,
        "client_secret": settings.story_api_client_secret,
        "grant_type": "client_credentials"
    }
    token: BearerToken = None
    endpoint: str = settings.story_api_login  # url + endpoint

    @staticmethod
    def sql_decorator(func):
        """ TODO: add parameter if MSSQL_SERVER defined """

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Check token in DB
            if (old_token := self.token) is None:
                repos = ClientsAndAuthRepositorySQL()
                if (old_token := repos.view(
                    {repos.primary_key: self.payload.get(repos.primary_key)}
                )) is not None:
                    self.token = BearerToken(**old_token.model_dump())

            token = func(self, *args, **kwargs)

            # extra ignored by def AND is token changed
            if token and (old_token is None or token.access_token != old_token.access_token):
                self.update_client_with_token()

            return token

        return wrapper

    def update_client_with_token(self):
        client_and_auth = AuthSQL(**(self.token.model_dump() | self.payload))
        ClientsAndAuthRepositorySQL().insert_update(client_and_auth)
        print(f"token updated: {self.token.expires_at}")

    def is_token_expired(self) -> bool:
        return self.token is None or self.token.expires_at < datetime.now(timezone.utc)

    @sql_decorator
    def get_token(self, *args, **kwargs) -> BearerToken | None:
        """the tokens have to be cached on the OAuth client side"""

        if not self.is_token_expired():
            return self.token

        response = None
        while True:
            try:
                # may return not valid token
                response = requests.request(
                    "POST",
                    settings.story_api_login,
                    headers=self.headers,
                    data=param_to_str(self.payload)
                )

                self.token = BearerToken(**response.json())

            except pydantic.ValidationError as e:
                print(str(e))
                print(str(response.json()))
                time.sleep(10)
                continue
            except requests.exceptions.JSONDecodeError:
                if response and response.status_code != 200:
                    raise requests.HTTPError(response=response)
                return None
            else:
                return self.token


class ABCStoryService(Generic[T], BearerService):
    """Abstract class for story service"""

    method: str = "GET"
    endpoint: str | None = None

    def __init__(self):
        super(ABCStoryService, self).__init__()
        self.model = get_args(self.__orig_bases__[0])[0]  # Magic

    def __new__(cls, *args, **kwargs):
        if cls.endpoint is None:
            raise NotImplementedError(f"Class must define {cls.endpoint=}")

        return super(ABCStoryService, cls).__new__(cls, *args, **kwargs)

    def get_url(self, *args, **kwargs) -> str:
        if not args:
            raise requests.exceptions.InvalidURL(f"{args=} for {self.endpoint=} are not defined")

        url = f"{settings.story_api_url}{self.endpoint}/{'/'.join(args)}"
        if kwargs:
            url = f"{url}?{param_to_str(param=kwargs)}"

        return url

    def get_story_api_data(self, *args, **kwargs) -> T | None:
        """Authorization:Bearer token
        :raises: TypeError, ValueError, requests.exceptions.InvalidURL
        """
        url = self.get_url(*args, **kwargs)
        while True:
            try:
                token = self.get_token()
                response = requests.request(
                    self.method,
                    url,
                    headers={"Authorization": f"{token.token_type} {token.access_token}"}
                )
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.SSLError) as e:
                # start from last bill
                print(f"Error {e}; sleep 10 sec")
                time.sleep(10)
            else:
                break

        try:
            res = self.model(**response.json())
        except TypeError as e:
            print(str(e))
            print(str(response.json()))
            return None
        except requests.exceptions.JSONDecodeError:
            return None
        else:
            return res
