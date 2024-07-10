"""
Storyous demo
API migration data without saving to MSSQL.
for test download stability & performance issues of API endpoints.
"""
from datetime import datetime, timedelta
from typing import List, Dict

from storyapi.config.settings import settings
from storyapi.db import SourceId
from storyapi.service.bills import BillsListAPI, BillsAPI
from storyapi.service.merchants import MerchantsAPI

bills_list_repo = BillsListAPI()
bills_api_repo = BillsAPI()


def get_merchant(mid):
    """take merchant from API by ID"""

    merchant = MerchantsAPI().get_story_api_data(mid)
    place = merchant.places.pop().place_id

    return merchant.merchant_id, place


def get_store_bills(source_id: SourceId):
    """ get BillsList from API & store in DB. Ignored if exists """

    while True:
        bills_list = bills_list_repo.get_story_api_data(source_id)
        for bll in bills_list.data:

            bll.place_id = source_id.place_id
            bill_id_list = [{"bill_id": bll.bill_id}]
            get_store_bill_details(bill_id_list, source)

        if not bills_list.nextPage:
            break
        source_id = bills_list.nextPage
        print(f"nextPage API request: {source_id=}")

    return source_id


def get_store_bill_details(
        bill_ids_list: List[Dict],
        source_id: SourceId
):
    """ request Bill details from API & store in DB """

    for bll in bill_ids_list:
        # bet Detailed Bill
        bll_details = bills_api_repo.get_story_api_data(source_id, bll.get("bill_id"))
        if not bll_details:
            print(f"Unable to get details for bill {bll.get('bill_id')}")
            continue
        # bill will not be updated;
        print(
            f"{bll_details.bill_id} {bll_details.created_at} "
            f"add items: {','.join([i.name for i in bll_details.items])}"
        )


if __name__ == '__main__':

    # check parameters

    # take merchant_id, place_id from API by ID
    merchant_id, place_id = get_merchant(settings.story_api_merchant_id)

    # prepare data for request
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

    # get all bill_id's from data range and ignore it on importing before send to DB
    get_store_bills(source)

    source.refunded = True
    source.last_bill_id = None

    get_store_bills(source)
