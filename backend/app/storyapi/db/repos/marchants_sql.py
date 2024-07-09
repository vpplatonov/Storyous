from common.db.mssql import RepositoryMSSQL
from storyapi.db.merchants_sql import AddressPartsSQL, PlacesSQL, MerchantsSQL


class AddressPartsRepositorySQL(RepositoryMSSQL[AddressPartsSQL]):
    primary_key = "place_id"
    pk_remove_on_create = False


class PlacesRepositorySQL(RepositoryMSSQL[PlacesSQL]):
    primary_key = "place_id"
    pk_remove_on_create = False
    excluded_fields = {"address_parts"}


class MerchantsRepositorySQL(RepositoryMSSQL[MerchantsSQL]):
    """ External primary key: do not pointed it """
    primary_key = "merchant_id"
    pk_remove_on_create = False
    excluded_fields = {"places"}
