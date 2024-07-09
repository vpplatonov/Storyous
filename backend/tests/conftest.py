import pytest
from storyapi.config.settings import settings


@pytest.fixture(name="bearer_token")
def get_token():
    return {
        "token_type": "Bearer",
        "expires_at": "2019-07-16T11:20:26.221Z",
        "access_token": "abcdeabcde.abcdeabcde.abcdeabcdeabcde"
    }


@pytest.fixture(name="mId")
def get_merchant_id():
    return settings.story_api_merchant_id
