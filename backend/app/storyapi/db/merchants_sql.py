from typing import Literal

from fastapi_utils.api_model import APIModel
from pydantic import Field

from common.db.mssql import RepositoryMSSQL


class AddressPartsSQL(APIModel):
    """ Same for AddressParts """

    place_id: str = Field(..., alias="place_id")
    street: str | None  # = "sdes"
    street_number: str | None = Field(default=None, alias="streetNumber")  # = "sdes"
    city: str | None   # = "Prague"
    country: str | None   # = "Czech republic"
    country_code: str | None = Field(default=None, alias="countryCode")
    zip: str | None  # = "18600",
    latitude: float | None  # = 50.073034
    longitude: float | None  # = 14.43618


class PlacesSQL(APIModel):
    merchant_id: str = Field(..., alias='merchantId')
    place_id: str = Field(..., alias='placeId')
    name: str  # = "My Super Bar"
    state: Literal["active", "disabled", "hidden"]  # = active | disabled | hidden


class MerchantsSQL(APIModel):
    client_id: str | None = None
    merchant_id: str = Field(..., alias='merchantId')
    name: str | None  # = "My Super Company"
    business_id: str = Field(..., alias='businessId')
    vat_id: str = Field(..., alias='vatId')  # = "CZ012345678"
    is_vat_payer: bool = Field(..., alias='isVatPayer')
    country_code: str = Field(..., alias='countryCode')  # = "CZ"
    currency_code: str = Field(..., alias='currencyCode')  # = "CZK"


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
