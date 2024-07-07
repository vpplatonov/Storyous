from datetime import datetime
from urllib.parse import unquote

from fastapi_utils.api_model import APIModel
from pydantic import Field, field_serializer, model_validator

from storyapi.config import ISO_FORMAT

source_set = {"merchant_id", 'place_id'}


class SourceId(APIModel):
    """
    sourceId: combination of merchantId and placeId, concatenated by dash
    Example: 5a75b658f60a3c15009312f1-5a75b658f60a3c15009312f2
    """
    merchant_id: str = Field(...)
    place_id: str = Field(...)
    from_date: datetime | None = Field(default=None, alias='from')
    till_date: datetime | None = Field(default=None, alias='till')
    limit: int | None = Field(default=None, alias='limit')
    last_bill_id: str | None = Field(default=None, alias='lastBillId')
    modified_since: datetime | None = Field(default=None, alias='modifiedSince')
    refunded: bool | None = Field(default=None, alias='refunded')

    def get_source_id(self) -> str:
        source_id = self.model_dump(include=source_set, by_alias=True)
        return '-'.join(list(source_id.values()))

    @staticmethod
    def parse_source_id(url_encoded: str):
        """ Parse url encoded string to SourceId

        :param url_encoded:
        :return: SourceId API Model
        """
        url, param = url_encoded.split('?')
        param_list = param.split('&')
        param_dict = {k: unquote(v) for pl in param_list for k, v in [tuple(pl.split('='))]}
        url, source_id = url.rsplit('/', 1)

        return SourceId(sourceId=source_id, **param_dict)  # Ignore

    @field_serializer('from_date', 'till_date', 'modified_since', when_used='always')
    def dump_datetime(self, v):
        return v.strftime(ISO_FORMAT)

    @model_validator(mode="before")
    def get_merchant_id(cls, v):
        if source_id := v.get('sourceId', None):
            v["merchant_id"], v["place_id"] = source_id.split('-')

        return v
