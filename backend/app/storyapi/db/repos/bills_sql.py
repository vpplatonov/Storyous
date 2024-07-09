from typing import Union, List, Dict

import pymssql
import pyodbc

from common.db.mssql import RepositoryMSSQL
from storyapi.db import SourceId
from storyapi.db.bills_sql import (
    TaxesSQL, PersonSQL, PaymentsSQL, OrderProviderSQL,
    FiscalDataSQL, InvoiceDataSQL, ItemsSQL, BillsSQL
)


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
            cursor: Union[pymssql.Cursor, pyodbc.Cursor]
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
