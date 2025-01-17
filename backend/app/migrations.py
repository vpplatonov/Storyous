"""
Storyous API migration data to MSSQL
"""
from datetime import datetime, timedelta
from typing import List, Dict

from common.db.mssql import CrudDataMSSQLError
from storyapi.config.settings import settings
from storyapi.db import SourceId
from storyapi.db.repos.bills_sql import BillsRepositorySQL
from storyapi.db.repos.marchants_sql import PlacesRepositorySQL, MerchantsRepositorySQL
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

    bills_list_repo = BillsListAPI()
    bills_repo = BillsRepositorySQL()

    while True:
        bills_list = bills_list_repo.get_story_api_data(source_id)
        for bll in bills_list.data:
            try:
                bll.place_id = source_id.place_id
                bills_repo.create_with_fk(bll)
                print(f"{bll.bill_id} {bll.created_at} imported")
            except CrudDataMSSQLError as e:
                # print(str(e))   # if DEBUG
                # already in DB
                print(f"Already in DB {bll.bill_id} {bll.created_at}")
                pass

        if not bills_list.next_page:
            break
        source_id = bills_list.next_page
        print(f"nextPage API request: {source_id=}")

    return source_id


def get_store_bills_batch(source_id: SourceId):
    """ get BillsList from API & store in DB. Ignored if exists """

    bills_list_repo = BillsListAPI()
    bills_repo = BillsRepositorySQL()

    while True:
        bills_list = bills_list_repo.get_story_api_data(source_id)
        bills_list.check_place_id(place_id=source_id.place_id)
        message = "\n".join([f"{bll.bill_id} {bll.created_at} imported" for bll in bills_list.data])
        try:
            bills_repo.create_batch_with_fk(bills_list.data)
            print(message)
        except CrudDataMSSQLError as e:
            # print(str(e))   # if DEBUG
            # already in DB
            print(f"Already in DB:\n{message}")
            pass

        if not bills_list.next_page:
            break
        source_id = bills_list.next_page


def get_store_bill_details(bill_ids_list: List[Dict], source_id: SourceId):
    """ request Bill details from API & store in DB """

    bills_api = BillsAPI()
    bills_repo = BillsRepositorySQL()

    for bll in bill_ids_list:
        # bet Detailed Bill
        bll_details = bills_api.get_story_api_data(source_id, bll.get("bill_id"))
        if not bll_details:
            print(f"Unable to get details for bill {bll.get('bill_id')}")
            continue
        # bill will be updated; other dependencies -> delete/insert
        bills_pk = BillsRepositorySQL.primary_key
        bills_repo.update_with_fk(
            bll_details, query={bills_pk: getattr(bll_details, bills_pk)}
        )
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
    # get_store_bills(source)
    get_store_bills_batch(source)

    # get list of imported bills from DB
    bills = BillsRepositorySQL().get_wo_items(source)
    get_store_bill_details(bills, source)

    source.refunded = True
    source.last_bill_id = None

    # get_store_bills(source)
    get_store_bills_batch(source)
    bills = BillsRepositorySQL().get_wo_items(source)
    get_store_bill_details(bills, source)
