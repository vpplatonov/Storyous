"""
Storyous API migration data to MSSQL
"""
from datetime import datetime, timedelta
from typing import List, Dict

from common.db.mssql import CrudDataMSSQLError
from storyapi.config.settings import settings
from storyapi.db import SourceId
from storyapi.db.bills_sql import BillsRepositorySQL
from storyapi.db.merchants_sql import MerchantsRepositorySQL, PlacesRepositorySQL
from storyapi.service.bills import BillsListAPI, BillsAPI
from storyapi.service.merchants import MerchantsAPI


def get_merchant(mid):
    """take merchant from DB or API by ID"""
    merch_repo_sql = MerchantsRepositorySQL()
    if merchant := merch_repo_sql.view(mid):
        places = PlacesRepositorySQL().index(
            filter={merch_repo_sql.primary_key: merchant.merchant_id}
        )
        place = places.pop().place_id

        return merchant.merchant_id, place

    merchant = MerchantsAPI().get_story_api_data(mid)
    # story merchant to MSSQL DB
    merch_repo_sql.create_with_fk(merchant)
    place = merchant.places.pop().place_id

    return merchant.merchant_id, place


def get_store_bills(source_id: SourceId):
    """ get BillsList from API & store in DB. Ignored if exists """

    while True:
        bills_list = BillsListAPI().get_story_api_data(source_id)
        for bll in bills_list.data:
            try:
                bll.place_id = source_id.place_id
                BillsRepositorySQL().create_with_fk(bll)
                print(f"{bll.bill_id=} imported")
            except CrudDataMSSQLError as e:
                # print(str(e))   # if DEBUG
                # already in DB
                print(f"Already in DB {bll.bill_id=}")
                pass

        if not bills_list.nextPage:
            break
        source_id = bills_list.nextPage
        print(f"nextPage API request: {source_id=}")

    return source_id


def get_store_bill_details(bill_ids_list: List[Dict], source_id: SourceId):
    """ request Bill details from API & store in DB """

    bills_api = BillsAPI()
    bills_repository = BillsRepositorySQL()
    bills_pk = BillsRepositorySQL.primary_key

    for bll in bill_ids_list:
        # bet Detailed Bill
        bll = bills_api.get_story_api_data(source_id, bll.get("bill_id"))
        # bill will be updated; other dependencies -> delete/insert
        bills_repository.update_with_fk(
            bll, query={bills_pk: getattr(bll, bills_pk)}
        )
        print(f"{bll.bill_id=} updated with items: {','.join([i.name for i in bll.items])}")


if __name__ == '__main__':

    # take merchant_id, place_id from API by ID
    merchant_id, place_id = get_merchant(settings.story_api_merchant_id)

    # prepare data for request
    source = SourceId(**dict(
        merchant_id=merchant_id,
        place_id=place_id,
        from_date=datetime.utcnow() - timedelta(
            weeks=10  # week == 1 return 7 bills
        ),  # ISO format,
        till_date=datetime.utcnow(),
        limit=20,
        refunded=True
    ))

    get_store_bills(source)

    # get list of imported bills from DB
    bills = BillsRepositorySQL().get_wo_items(source)
    get_store_bill_details(bills, source)
