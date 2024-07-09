from storyapi.db.auth import BearerToken, AuthSQL
from storyapi.service.auth import get_token


def test_bearer_token(bearer_token):
    token = BearerToken(**bearer_token)

    assert token is not None
    assert isinstance(token, BearerToken)

    client = AuthSQL(**token.model_dump())
    assert client is not None
    assert isinstance(client, AuthSQL)


def test_bearer_service(bearer_token):

    token = get_token()
    assert token is not None
    assert isinstance(token, BearerToken)

    token2 = get_token()
    assert token2 is not None
    assert token2 == token

    token3 = get_token()
    assert token3 is not None
    assert token2 == token3
