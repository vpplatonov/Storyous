import pytest

from storyapi.config import param_to_str
from storyapi.db.repos.bills_sql import BillsRepositorySQL
from storyapi.service.auth import ABCStoryService
from storyapi.db.bills import (
    BillsList, Bills
)
from storyapi.service.bills import BillsAPI, BillsListAPI
from storyapi.db import source_set, SourceId
from storyapi.db.merchants import Merchant
from storyapi.service.merchants import MerchantsAPI


@pytest.fixture(name="source_url_encoded")
def get_source_url_encoded():
    return (
        'https://api.storyous.com/bills/'
        '5a75b658f60a3c15009312f1-5a75b658f60a3c15009312f2'
        '?from=2016-06-19T10%3A32%3A01Z'
        '&till=2017-06-19T10%3A32%3A01Z'
        '&limit=10'
        '&lastBillId=BA2018000001'
        '&modifiedSince=2016-06-19T10%3A32%3A01Z'
        '&refunded=true'
    )


@pytest.fixture(name="source_id")
def get_source_id(source_url_encoded):
    return SourceId.parse_source_id(source_url_encoded)


@pytest.fixture(name="bills_list")
def get_bills_list():
    return {
        "data": [
            {
                "billId": "BA2018000001",
                "sessionCreated": "2018-08-03T14:59:46+02:00",
                "createdAt": "2018-08-03T14:59:48+02:00",
                "paidAt": "2018-08-03T14:59:47+02:00",
                "fiscalizedAt": None,
                "finalPrice": "150.4",
                "finalPriceWithoutTax": "8.26",
                "taxSummaries": {
                    "15": "1.74"
                },
                "taxes": [
                    {
                        "vat": "15",
                        "totalVat": "1.74",
                        "totalWithoutVat": "8.26"
                    }
                ],
                "discount": "0.00",
                "rounding": "0.00",
                "tips": "0.00",
                "currencyCode": "CZK",
                "refunded": False,
                "paymentMethod": "split",
                "payments": [
                    {
                        "paymentMethod": "cash",
                        "priceWithVat": "100"
                    },
                    {
                        "paymentMethod": "card",
                        "priceWithVat": "50.4"
                    }
                ],
                "createdBy": {
                    "personId": 2187839,
                    "fullName": "Person full name",
                    "userName": "username"
                },
                "paidBy": {
                    "personId": 2187839,
                    "fullName": "Person full name",
                    "userName": "username"
                },
                "personCount": 1,
                "deskId": None,
                "issuedAsVatPayer": False,
                "fiscalData": [],
                "invoiceData": [],
                "customerId": None,
                "orderProvider": {
                    "code": "dj",
                    "orderId": "5a75b658f60a3c15009312f1",
                },
                "_lastModifiedAt": "2018-08-03T14:59:47+02:00"
            }
        ],
        "nextPage": "/bills/60b6512e66943300381c2d24-60b6512e66943300381c2d25?from=2024-04-29T00%3A00%3A00.000Z&till=2024-07-08T23%3A59%3A59.000Z&limit=20&refunded=1&lastBillId=TM2024019684",
        "ok": 1
    }


@pytest.fixture(name="bill_detail")
def get_bill_details():
    return {
        "billId": "KB2018007144",
        "sessionCreated": "2018-04-20T14:48:29+02:00",
        "createdAt": "2018-04-20T14:49:03+02:00",
        "paidAt": "2018-04-20T14:49:02+02:00",
        "fiscalizedAt": "2018-04-20T14:49:07+02:00",
        "finalPrice": "10.00",
        "finalPriceWithoutTax": "8.26",
        "taxSummaries": {
            "15": "1.74"
        },
        "taxes": [
            {
                "vat": "15",
                "totalVat": "1.74",
                "totalWithoutVat": "8.26"
            }
        ],
        "discount": "0.00",
        "rounding": "0.00",
        "tips": "0.00",
        "currencyCode": "CZK",
        "refunded": False,
        "paymentMethod": "cash",
        "payments": [
            {
                "paymentMethod": "cash",
                "priceWithVat": "10"
            }
        ],
        "createdBy": {
            "personId": 2187839,
            "fullName": "George Bush",
            "userName": "thegeorgebush"
        },
        "paidBy": {
            "personId": 2187839,
            "fullName": "Slide a Lama",
            "userName": "theslidealama"
        },
        "personCount": 1,
        "deskId": None,
        "issuedAsVatPayer": True,
        "fiscalData": {
            "mode": 1,
            "endpoint": "https://prod.eet.cz:443/eet/services/EETServiceSOAP/v3",
            "fik": "4974d3d2-3adb-4608-b046-a51f47829fff-01",
            "pkp": "JXMIBqSrrfwefregeg8qW9Uncr6VgLa9kWlV+1H1/dxN98qWq3W9r85RkawllTlJnrmSc/VZu9LPy5Uofsoo1ZAFUwe+ZVZ7qDKa8ZPZGFV9lAm+C8v0ze8KXrmmxjY5UVyVnoWaB2UFyHE1aw/cUjqj5zmW7O/T+V5/u/q7kmWf2CVA4FfioWQDxsc1L0noQReL64oYmgKiZPfuFDZcdlH41gWG5mc+n0a5WMfDZXZOoAXIwAGxw67w9/WzG7hKZePk4T5kqvsFthsyKh/1gwJCxy8fKkmBYRHyzn0TclwRrToPZk1RU0hfrcyG81hqYqdKRRmkyWM/mQCzSYxrQ==",
            "bkp": "daf0575c-5fde4f72-d96778f6-06455d77-b115f6ff",
            "httpStatusCode": 200
        },
        "invoiceData": None,
        "customerId": None,
        "orderProvider": {
            "code": "dj",
            "orderId": "5a75b658f60a3c15009312f1",
        },
        "items": [
            {
                "name": "Hotdog",
                "amount": 1,
                "measure": "pcs",
                "price": 5,
                "vatRate": 0.15,
                "productId": "p:xf75Uew",
                "decodedId": 54,
                "categoryId": "c:abcdfes",
                "hasAdditionsWithCode": None,
                "additionsCode": None,
                "ean": "012345678910"
            },
            {
                "name": "Pizza",
                "amount": 1,
                "measure": "pcs",
                "price": 55,
                "vatRate": 0.15,
                "productId": "p:ief75ew",
                "decodedId": 88,
                "categoryId": "c:sijsfjwd",
                "hasAdditionsWithCode": "00e99787-2939-417a-b043-6047ceb0117d",
                "additionsCode": None,
                "ean": None
            },
            {
                "name": "Extra cheese on pizza",
                "amount": 1,
                "measure": "pcs",
                "price": 15,
                "vatRate": 0.15,
                "productId": "p:taHFmNmJt",
                "decodedId": 65,
                "categoryId": None,
                "hasAdditionsWithCode": None,
                "additionsCode": "00e99787-2939-417a-b043-6047ceb0117d",
                "ean": None
            }
        ]
    }


def test_abc_story_service():
    with pytest.raises(NotImplementedError) as e:
        ABCStoryService()

    assert "Class must define" in str(e.value)


def test_merchants(mId):
    serv = MerchantsAPI()
    assert isinstance(serv, MerchantsAPI)

    res = serv.get_story_api_data(mId)
    assert isinstance(res, Merchant)


def test_source_id(source_id: SourceId):
    assert isinstance(source_id, SourceId)

    source = source_id.model_dump(include=source_set, by_alias=True)
    source = '-'.join(list(source.values()))
    assert isinstance(source, str)

    source_dump = source_id.model_dump(exclude=source_set, by_alias=True, exclude_none=True)
    source_url = param_to_str(param=source_dump)

    assert isinstance(source_dump, dict)
    assert isinstance(source_url, str)


def test_bills(bills_list, source_id: SourceId, source_url_encoded: str):
    bills = BillsList(**bills_list)
    assert isinstance(bills, BillsList)

    url = BillsListAPI().get_url(source_id)
    assert isinstance(url, str)
    assert url == source_url_encoded

    url = BillsListAPI().get_url(bills.next_page)
    assert isinstance(url, str)


def test_bill_details(source_id, bill_detail):
    bill = Bills(placeId=source_id.place_id, **bill_detail)
    assert isinstance(bill, Bills)

    url = BillsAPI().get_url(source_id, bill.bill_id)
    assert isinstance(url, str)

    bill.place_id = source_id.place_id
    BillsRepositorySQL().create_with_fk(bill)
