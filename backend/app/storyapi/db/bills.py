import json
from typing import List, Any

from fastapi_utils.api_model import APIModel
from pydantic import Field, model_validator

from storyapi.db import SourceId
from storyapi.db.bills_sql import (
    TaxesSQL, PersonSQL, PaymentsSQL, OrderProviderSQL,
    FiscalDataSQL, InvoiceDataSQL, ItemsSQL, BillsSQL
)


class Taxes(TaxesSQL):
    """ Same as TaxesSQL """


class Person(PersonSQL):
    """ Same as PersonSQL """


class Payments(PaymentsSQL):
    """ Same as PaymentSQL """


class OrderProvider(OrderProviderSQL):
    """ same as OrderProviderSQL """


class FiscalData(FiscalDataSQL):
    """ Same as FiscalData """


class InvoiceData(InvoiceDataSQL):
    """ same as InvoiceDataSQL """


class Items(ItemsSQL):
    """ same as ItemsSQL """


class Bills(BillsSQL):
    place_id: str = Field(
        default=None,
        alias='place',
        json_schema_extra=dict(primary_key="place_id")
    )
    taxes: List[Taxes] | None = Field(
        default=None,
        alias='taxes',
        exclude=True,
        json_schema_extra=dict(foreign_key="bill_id")
    )
    payments: List[Payments] | None = Field(
        default=None,
        alias='payments',
        exclude=True,
        json_schema_extra=dict(foreign_key="bill_id")
    )
    created_by: Person | int = Field(
        ...,
        alias='createdBy',
        json_schema_extra=dict(primary_key="person_id")
    )
    paid_by: Person | int = Field(
        ...,
        alias='paidBy',
        json_schema_extra=dict(primary_key="person_id")
    )
    fiscal_data: List[FiscalData] | None = Field(
        default=None,
        alias='fiscalData',
        exclude=True,
        json_schema_extra=dict(foreign_key="bill_id")
    )
    invoice_data: List[InvoiceData] | None = Field(
        default=None,
        alias='invoiceData',
        exclude=True,
        json_schema_extra=dict(foreign_key="bill_id")
    )
    order_provider: List[OrderProvider] | None = Field(
        default=None,
        alias='orderProvider',
        exclude=True,
        json_schema_extra=dict(foreign_key="bill_id")
    )
    items: List[Items] | None = Field(
        default=None,
        alias='items',
        exclude=True,
        json_schema_extra=dict(foreign_key="bill_id")
    )

    @model_validator(mode="before")
    def fill_empty_fields(cls, v):
        if lma := v.get("_lastModifiedAt"):
            v["lastModifiedAt"] = lma

        bill_id = v.get("billId", None)
        if bill_id and v.get("taxes", None):
            for i in range(len(v["taxes"])):
                v["taxes"][i]["bill_id"] = bill_id

        if bill_id and v.get("payments", None):
            for i in range(len(v["payments"])):
                v["payments"][i]["bill_id"] = bill_id

        if bill_id and v.get("items", None):
            for i in range(len(v["items"])):
                v["items"][i]["bill_id"] = bill_id

        if (fiskd := v.get("fiscalData")) is not None and isinstance(fiskd, dict):
            if bill_id:
                fiskd["bill_id"] = bill_id
            v["fiscalData"] = [fiskd]

        if (ordprov := v.get("orderProvider")) is not None and isinstance(ordprov, dict):
            if bill_id:
                ordprov["bill_id"] = bill_id
            v["orderProvider"] = [ordprov]

        if (idata := v.get("invoiceData")) is not None and isinstance(idata, dict):
            if bill_id:
                idata["bill_id"] = bill_id
            idata["data"] = json.dumps(idata, default=str)
            v["invoiceData"] = [idata]

        return v


class BillsList(APIModel):
    """
    nextPage: "/bills/5a75b658f60a3c15009312f1-5a75b658f60a3c15009312f2?lastBillId=BA2018000001"
    """
    data: List[Bills] = Field(default_factory=list, alias='data')
    nextPage: Any | None
    ok: bool | None = Field(default=None)

    @model_validator(mode="before")
    def fill_empty_fields(cls, v):
        if (next_page := v.get("nextPage", None)) is not None and isinstance(next_page, str):
            source = SourceId.parse_source_id(next_page)
            for i in range(len(v["data"])):
                v["data"][i]["place_id"] = source.place_id
            v["nextPage"] = source

        return v
