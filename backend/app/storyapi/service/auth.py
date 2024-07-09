import functools
import time
from datetime import datetime, timezone
from typing import Generic, get_args

import pydantic
import requests

from common.config import T
from storyapi.config import param_to_str
from storyapi.config.settings import settings
from storyapi.db.auth import BearerToken, AuthSQL
if settings.mssql_server:
    from storyapi.db.auth import ClientsAndAuthRepositorySQL


headers: dict = {
    "Content-Type": "application/x-www-form-urlencoded"
}
# Body: must be merged by & sign
payload: dict = {
    "client_id": settings.story_api_client_id,
    "client_secret": settings.story_api_client_secret,
    "grant_type": "client_credentials"
}


def sql_enabled_decorator(func):
    """ parameter if MSSQL_SERVER defined """
    @functools.wraps(func)
    def wrapper(token: BearerToken = None):
        # Check token in DB
        # token = token or wrapper.token
        if (old_token := token) is None and settings.mssql_server:
            repos = ClientsAndAuthRepositorySQL()
            if (old_token := repos.view(
                {repos.primary_key: payload.get(repos.primary_key)}
            )) is not None:
                token = BearerToken(**old_token.model_dump())

        token = func(token=token)

        # extra ignored by def AND is token changed
        if token and (old_token is None or token.access_token != old_token.access_token):
            # wrapper.token = token
            if settings.mssql_server:
                update_client_with_token(token)

        return token

    # wrapper.token = None
    return wrapper


def update_client_with_token(token):
    client_and_auth = AuthSQL(**(token.model_dump() | payload))
    ClientsAndAuthRepositorySQL().insert_update(client_and_auth)


def is_token_expired(token) -> bool:
    return token is None or token.expires_at < datetime.now(timezone.utc)


@sql_enabled_decorator
def get_token(token: BearerToken = None) -> BearerToken | None:
    """the tokens have to be cached on the OAuth client side"""

    if not is_token_expired(token):
        return token

    response = None
    while True:
        try:
            # may return not valid token
            response = requests.request(
                "POST",
                settings.story_api_login,
                headers=headers,
                data=param_to_str(payload)
            )

            token = BearerToken(**response.json())

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
            print(f"token changed {token.expires_at=}")
            return token


class ABCStoryService(Generic[T]):
    """Abstract class for story service"""

    method: str = "GET"
    endpoint: str | None = None
    token: BearerToken = get_token()

    def __init__(self):
        # super(ABCStoryService, self).__init__()
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
        response = None
        while True:
            try:
                token = get_token(token=self.token)
                response = requests.request(
                    self.method,
                    url,
                    headers={"Authorization": f"{token.token_type} {token.access_token}"}
                )
                res = self.model(**response.json())
                self.token = token

            except TypeError as e:
                print(str(e))
                if response and response.status_code == 200:
                    print(str(response.json()))
                return None
            except requests.exceptions.JSONDecodeError:
                if response and response.status_code == 200:
                    print(str(response.text))
                return None
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.SSLError) as e:
                # start from last bill
                print(f"Error {e}; sleep 10 sec")
                time.sleep(10)
            else:
                return res
