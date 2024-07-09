from storyapi.db.auth import BearerToken, AuthSQL
from storyapi.service.auth import BearerService


def test_bearer_token(bearer_token):
    token = BearerToken(**bearer_token)

    assert token is not None
    assert isinstance(token, BearerToken)

    client = AuthSQL(**token.model_dump())
    assert client is not None
    assert isinstance(client, AuthSQL)


def test_bearer_service(bearer_token):
    service = BearerService()
    assert service is not None

    token = service.get_token()
    assert token is not None
    assert isinstance(token, BearerToken)
