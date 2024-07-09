import json
from datetime import datetime
from typing import Literal, Union, List, Dict

from fastapi_utils.api_model import APIModel
from pydantic import Field, field_validator

from common.config import settings

if settings.mssql_server:
    from pymssql import Cursor as pymssql_Cursor
    from pyodbc import Cursor as pyodbc_Cursor
    from common.db.mssql import RepositoryMSSQL

from storyapi.config import convert_datetime
from storyapi.db import SourceId


class TaxesSQL(APIModel):
    pid: int | None = None
    bill_id: str = Field(..., alias='billId')
    vat: float | None = Field(..., alias='vat')
    total_vat: float | None = Field(..., alias='totalVat')
    total_without_vat: float | None = Field(..., alias='totalWithoutVat')


class PersonSQL(APIModel):
    """ use person_id field as primary key """
    person_id: int = Field(..., alias='personId')
    full_name: str = Field(..., alias='fullName')
    user_name: str = Field(..., alias='userName')


class PaymentsSQL(APIModel):
    pid: int | None = None
    bill_id: str = Field(..., alias='billId')
    payment_method: Literal["cash", "card", "split", "bank"] = Field(
        ...,
        alias='paymentMethod'
    )
    price_with_vat: float = Field(..., alias='priceWithVat')


class OrderProviderSQL(APIModel):
    pid: int | None = None
    bill_id: str = Field(..., alias='billId')
    code: str
    order_id: str | None = Field(default=None, alias='orderId')


class FiscalDataSQL(APIModel):
    pid: int | None = None
    bill_id: str = Field(..., alias='billId')
    mode: int | str | None  # 1,
    endpoint: str  # "https://prod.eet.cz:443/eet/services/EETServiceSOAP/v3",
    fik: str  # "4974d3d2-3adb-4608-b046-a51f47829fff-01",
    pkp: str  # "JXMIBqSrrfwefregeg8qW9Uncr6VgLa9kWlV+1H1/dxN98qWq3W9r85RkawllTlJnrmSc/VZu9LPy5Uofsoo1ZAFUwe+ZVZ7qDKa8ZPZGFV9lAm+C8v0ze8KXrmmxjY5UVyVnoWaB2UFyHE1aw/cUjqj5zmW7O/T+V5/u/q7kmWf2CVA4FfioWQDxsc1L0noQReL64oYmgKiZPfuFDZcdlH41gWG5mc+n0a5WMfDZXZOoAXIwAGxw67w9/WzG7hKZePk4T5kqvsFthsyKh/1gwJCxy8fKkmBYRHyzn0TclwRrToPZk1RU0hfrcyG81hqYqdKRRmkyWM/mQCzSYxrQ==",
    bkp: str  # "daf0575c-5fde4f72-d96778f6-06455d77-b115f6ff",
    http_status_code: int | str | None = Field(
        ...,
        alias='httpStatusCode'
    )


class InvoiceDataSQL(APIModel):
    pid: int | None = None
    bill_id: str = Field(..., alias='billId')
    data: str | None = Field(default=None, alias='data')


class ItemsSQL(APIModel):
    pid: int | None = None
    bill_id: str = Field(..., alias='billId')
    name: str  # Hotdog,
    amount: float  # 1,
    measure: str  # pcs,
    price: float  # 5,
    vat_rate: float = Field(..., alias='vatRate')
    product_id: str = Field(..., alias='productId')  # p:xf75Uew,
    decoded_id: int = Field(..., alias='decodedId')  # 54,
    category_id: str | None = Field(..., alias='categoryId')
    has_additions_with_code: str | None = Field(..., alias='hasAdditionsWithCode')
    additions_code: str | None = Field(..., alias='additionsCode')
    ean: str | None = None  # 012345678910


class BillsSQL(APIModel):
    """ Add place_id field for relation between Bills and Person """
    place_id: str | None = Field(default=None, alias='placeId')
    bill_id: str = Field(..., alias='billId')
    session_created: datetime | None = Field(default=None, alias='sessionCreated')
    created_at: datetime | None = Field(default=None, alias='createdAt')
    paid_at: datetime | None = Field(default=None, alias='paidAt')
    fiscalized_at: datetime | None = Field(default=None, alias='fiscalizedAt')
    final_price: float = Field(..., alias='finalPrice')
    final_price_without_tax: float = Field(..., alias='finalPriceWithoutTax')
    tax_summaries: dict = Field(..., alias='taxSummaries')
    discount: float = Field(default=0, alias='discount')
    rounding: float = Field(default=0, alias='rounding')
    tips: float = Field(default=0, alias='tips')
    currency_code: str = Field(..., alias='currencyCode')
    refunded: bool | None = Field(default=None, alias='refunded')
    payment_method: Literal["cash", "card", "split", "bank"] = Field(..., alias='paymentMethod')
    created_by: int | None = Field(default=None, alias='createdBy')
    paid_by: int | None = Field(default=None, alias='paidBy')
    person_count: int = Field(default=1, alias='personCount')
    desk_id: int | str | None = Field(default=None, alias='deskId')
    issued_as_vat_payer: bool = Field(..., alias='issuedAsVatPayer')
    customer_id: str | None = Field(default=None, alias='customerId')
    last_modified_at: datetime | None = Field(default=None, alias='lastModifiedAt')

    @field_validator("tax_summaries")
    def tax_summary(cls, v):
        if isinstance(v, dict):
            v = json.dumps(v)
        return v

    @field_validator(
        'session_created', 'paid_at', 'fiscalized_at', 'last_modified_at', 'created_at',
        mode='before'
    )
    def convert_datetime(cls, v):
        return convert_datetime(v)


if settings.mssql_server:
    class TaxesRepositorySQL(RepositoryMSSQL[TaxesSQL]):
        """ Use DB_PRIMARY_KEY as default primary key """


    class PersonRepositorySQL(RepositoryMSSQL[PersonSQL]):
        """ External primary key: do not pointed it """
        pk_remove_on_create = False
        primary_key = "person_id"


    class PaymentsRepositorySQL(RepositoryMSSQL[PaymentsSQL]):
        """ Use DB_PRIMARY_KEY as default primary key """


    class OrderProviderRepositorySQL(RepositoryMSSQL[OrderProviderSQL]):
        """ Use DB_PRIMARY_KEY as default primary key """


    class FiscalDataRepositorySQL(RepositoryMSSQL[FiscalDataSQL]):
        """ Use DB_PRIMARY_KEY as default primary key """


    class InvoiceDataRepositorySQL(RepositoryMSSQL[InvoiceDataSQL]):
        """ Use DB_PRIMARY_KEY as default primary key """


    class ItemsRepositorySQL(RepositoryMSSQL[ItemsSQL]):
        """ Use DB_PRIMARY_KEY as default primary key """


    class BillsRepositorySQL(RepositoryMSSQL[BillsSQL]):
        """ External primary key: do not pointed it """
        pk_remove_on_create = False
        primary_key = "bill_id"
        excluded_fields = {
            "taxes", "payments", "fiscal_data",
            "invoice_data", "order_provider", "items"
        }

        def converted_select_insert(
                self,
                convert_data,
                cursor: Union[pymssql_Cursor, pyodbc_Cursor]
        ):
            """ must be implemented for apps specific """
            rs = self._converted_select_insert(convert_data, cursor)

            return rs

        def get_wo_items(self, source: SourceId = None) -> List[Dict]:
            """
            :return:
            """

            sql_query = """
            SELECT bill_id
            FROM storyous.bills
            WHERE NOT EXISTS(SELECT 1 FROM storyous.items 
                    WHERE items.bill_id = bills.bill_id) 
            """ + f"""
                AND {self.json_to_sql.field_value_parser(source.from_date, div='')} <= bills.created_at
                AND {self.json_to_sql.field_value_parser(source.till_date, div='')} >= bills.created_at
            """ if source else ""

            data = self.exec_fetch_all(sql_query)

            return data
