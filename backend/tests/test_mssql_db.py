from datetime import datetime, timedelta

import pytest

from migrations import get_merchant, get_store_bills, get_store_bill_details
from storyapi.config.settings import settings
from storyapi.db import SourceId
from storyapi.db.auth import ClientsAndAuthRepositorySQL, AuthSQL
from storyapi.db.bills_sql import BillsRepositorySQL
from storyapi.db.merchants_sql import MerchantsRepositorySQL
from storyapi.service.merchants import MerchantsAPI


@pytest.fixture(name="merchant_sql")
def get_bills_sql(mId):
    serv = MerchantsAPI()
    res = serv.get_story_api_data(mId)
    return res


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
    # if (merchant := MerchantsRepositorySQL().view({
    #     "merchant_id": merchant_sql.merchant_id
    # })) is None:
    res = MerchantsRepositorySQL().create_with_fk(merchant_sql)
    assert res is not None


def test_get_store_bills(mId):
    merchant_id, place_id = get_merchant(mId)
    source = SourceId(**dict(
        merchant_id=merchant_id,
        place_id=place_id,
        from_date=datetime.combine(datetime.utcnow(), datetime.min.time()) - timedelta(
            weeks=10
        ),  # ISO format,
        till_date=datetime.combine(datetime.utcnow(), datetime.max.time()),
        limit=20,
        refunded=True
    ))

    last_source = get_store_bills(source)
    assert last_source is not None

    bills = BillsRepositorySQL().get_wo_items(source)
    assert isinstance(bills, list)
    get_store_bill_details(bills, source)
