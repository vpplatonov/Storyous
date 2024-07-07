import re
from datetime import datetime
from typing import Any
from urllib.parse import quote

ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
ISO_FORMAT2 = '%Y-%m-%dT%H:%M:%S.%fZ'
ISO_FORMAT3 = '%Y-%m-%dT%H:%M:%S%z'
# for validating date and times in ISO8601 format
regex = (
    r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])'
    r'T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)'
    r'?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
)
match_iso8601 = re.compile(regex).match


def validate_iso8601(str_val):
    try:
        if match_iso8601(str_val) is not None:
            return True
    except Exception:
        pass
    return False


def param_to_str(param: dict, bool_quoted: bool = False) -> str:
    """ Convert kwargs to k=v&k1=v1&... with url encoding """

    if not param:
        return ''
    return "&".join([
        f"{k}={quote(val_to_str(v, bool_quoted))}"
        for k, v in param.items()
    ])


def val_to_str(val, bool_quoted: bool = False) -> Any:
    """ Convert None to null & True/False to 'true'/'false' """

    if val is None:
        return 'null'
    if isinstance(val, str):
        return val
    if isinstance(val, bool):
        val = "true" if val else "false"
        if bool_quoted:
            return f"'{val}'"
        return val
    if isinstance(val, int):
        return str(val)


def convert_datetime(v: str) -> datetime | str:
    """ v string like ISO formatted
    TODO: datetime.fromisoformat() ?

    :return: datetime if valid ISO format; otherwise str
    """

    if v and validate_iso8601(v):
        if '.' in v:
            return datetime.strptime(v, ISO_FORMAT2)
        if '+' in v:
            return datetime.strptime(v, ISO_FORMAT3)
        return datetime.strptime(v, ISO_FORMAT)

    return v
