import json
from datetime import datetime, timedelta

import pytest

from migrations import get_merchant
from storyapi.config.settings import settings
from storyapi.db import SourceId
from storyapi.db.auth import AuthSQL
from storyapi.db.bills import BillsList
from storyapi.db.repos.auth import ClientsAndAuthRepositorySQL
from storyapi.db.merchants import Merchant
from storyapi.db.merchants_sql import MerchantsSQL
from storyapi.db.repos.bills_sql import BillsRepositorySQL
from storyapi.db.repos.marchants_sql import MerchantsRepositorySQL
from storyapi.service.bills import BillsListAPI


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


@pytest.fixture(name="merchant_place")
def get_merchant_place(mId):
    merchant_id, place_id = get_merchant(mId)

    return merchant_id, place_id


@pytest.fixture(name="source_id_work")
def get_source_id_work(merchant_place):
    merchant_id, place_id = merchant_place
    source = SourceId(**dict(
        merchant_id=merchant_id,
        place_id=place_id,
        from_date=datetime.utcnow() - timedelta(
            days=2  # week == 1 return 7 bills
        ),  # ISO format,
        till_date=datetime.utcnow(),
        limit=10,
        refunded=False
    ))

    return source


@pytest.fixture(name="json_filename")
def get_json_filename():
    """ file name w/o extension """
    filename = 'bills_list'
    return filename


@pytest.fixture(name="load_test_json")
def get_test_json(source_id_work, json_filename):
    with open(f'./source/json/{json_filename}.json') as f:
        json_str = f.read()
        test_json = json.loads(json_str)
        # test_json = json.dumps(d)

    return test_json


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


def test_store_batch(load_test_json, source_id_work):
    next_page = load_test_json["nextPage"]
    load_test_json["nextPage"] = None
    bills_list = BillsList(**load_test_json)
    assert isinstance(bills_list, BillsList)
    assert bills_list.data[0].place_id is None
    bills_list.check_place_id(place_id=source_id_work.place_id)
    assert bills_list.data[0].place_id is not None

    load_test_json["nextPage"] = next_page

    bills_list = BillsList(**load_test_json)
    assert isinstance(bills_list, BillsList)
    assert bills_list.data[0].place_id is not None
    bills_list.check_place_id(place_id=source_id_work.place_id)
    BillsRepositorySQL().create_batch_with_fk(bills_list.data)

