from datetime import datetime, timedelta

import pytest

from storyapi.config.settings import settings
from storyapi.db import SourceId
from storyapi.db.auth import AuthSQL
from storyapi.db.repos.auth import ClientsAndAuthRepositorySQL
from storyapi.db.merchants import Merchant
from storyapi.db.merchants_sql import MerchantsSQL
from storyapi.db.repos.marchants_sql import MerchantsRepositorySQL


@pytest.fixture(name="merchant_sql")
def get_bills_sql(mId):
    # data from OSS link:
    # https://apistoryouscom.docs.apiary.io/#reference/0/merchant/get-merchant-and-all-its-places
    res = {
      "merchantId": "57dab243332f920e00b6cc17",
      "name": "My Super Company",
      "businessId": "012345678",
      "vatId": "CZ012345678",
      "isVatPayer": True,
      "countryCode": "CZ",
      "currencyCode": "CZK",
      "places": [
        {
          "placeId": "5836b6981730220e00d7c8b5",
          "name": "My Super Bar",
          "state": "active",
          "addressParts": {
            "street": "sdfsdf",
            "streetNumber": "sdfsdf",
            "city": "Prague",
            "country": "Czech republic",
            "countryCode": "CZ",
            "zip": "18600",
            "latitude": 50.073034,
            "longitude": 14.43618
          }
        }
      ]
    }

    return Merchant(**res)


def test_client_and_auth():
    repos = ClientsAndAuthRepositorySQL()
    auth_list = repos.index()

    assert auth_list is not None
    assert len(auth_list) == 1

    client = repos.view({
        repos.primary_key: settings.story_api_client_id
    })
    assert isinstance(client, AuthSQL)


def test_merchant(merchant_sql):
    repos = MerchantsRepositorySQL()
    if (merchant := repos.view({
        repos.primary_key: getattr(merchant_sql, repos.primary_key)
    })) is None:
        res = repos.create_with_fk(merchant_sql)
        assert res is not None
    else:
        assert isinstance(merchant, MerchantsSQL)


def test_get_store_bills(merchant_sql):

    source = SourceId(**dict(
        merchant_id=merchant_sql.merchant_id,
        place_id=merchant_sql.places.pop().place_id,
        from_date=datetime.combine(datetime.utcnow(), datetime.min.time()) - timedelta(
            weeks=10
        ),  # ISO format,
        till_date=datetime.combine(datetime.utcnow(), datetime.max.time()),
        limit=20,
        refunded=True
    ))

    assert isinstance(source, SourceId)
