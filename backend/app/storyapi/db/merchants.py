from typing import List

from pydantic import Field, field_validator, model_validator

from storyapi.config.settings import settings
from storyapi.db.auth import ClientsAndAuthRepositorySQL, AuthSQL
from storyapi.db.merchants_sql import AddressPartsSQL, PlacesSQL, MerchantsSQL


class AddressParts(AddressPartsSQL):
    """ Same for AddressPartsSQL """


class Places(PlacesSQL):
    """ SQL Out : Place name: The Miners Borislavka """
    addressParts: AddressParts = Field(
        default=None,
        exclude=True,
        alias="AddressParts",
        json_schema_extra=dict(foreign_key="place_id")
    )

    @model_validator(mode='before')
    def check_address_parts(cls, values):
        if values and (place_id := values.get("placeId", None)) is not None \
                and 'addressParts' in values:
            values['addressParts']["place_id"] = place_id  # ignore

            return values


class Merchant(MerchantsSQL):
    """
    MechantID: 60b6512e66943300381c2d24
    PlaceID: 60b6512e66943300381c2d25
    """
    client_id: AuthSQL | str | None = Field(
        ...,
        json_schema_extra=dict(primary_key="client_id")
    )
    places: List[Places] = Field(
        default_factory=list,
        exclude=True,
        json_schema_extra=dict(foreign_key="merchant_id")
    )

    @field_validator("places", mode='before')
    def check_places(cls, value: list[dict] | dict | None, values) -> list[dict] | None:
        """ values: ValidationInfo. values.data keep the structure """
        if value and (merchant_id := values.data.get("merchant_id", None)) is not None:
            for p in value:
                p["merchantId"] = merchant_id

            return value

    @model_validator(mode='before')
    def check_client_id(cls, values) -> AuthSQL | None:
        # reading from DB init
        client_id = values.get("client_id", None)
        if client_id is None:
            client_id = settings.story_api_client_id

        if client_id is not None:
            values["client_id"] = ClientsAndAuthRepositorySQL().view({
                "client_id": client_id
            })
            values["client_id"].secret = ''
            values["client_id"].access_token = ''

        return values
