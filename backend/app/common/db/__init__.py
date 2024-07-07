import importlib
from datetime import datetime
from typing import Optional

from fastapi_utils.api_model import APIModel, PYDANTIC_VERSION
from pydantic import Field, ConfigDict

DEFAULT_DB_NAME_SPACE = 'storyous'
COUNT_FIELD = "count"
NUM_UPDATE_FIELD = "num_rows"
DB_PRIMARY_KEY = "pid"
SCHEMA_BY_ALIAS = False
SQL_REPOSITORY_POSTFIX = "RepositorySQL"
__version__ = "0.1.0"
__author__ = "Valerii Platonov"


def get_repository_for_model(
        model_type: str,
        prefix: str = '',
        plugin='merchants',
        package="storyapi.db"  # Class.__module__.rsplit('.', maxsplit=1)[0]
):
    """ Get Repository Module name (plugin) by class __name__ & __module__

    :parameter: model_type: Class.__name__
    :parameter::plugin: Class.__module__.rsplit('.', maxsplit=1)[1]
    :parameter::package: Class.__module__.rsplit('.', maxsplit=1)[0]
    :raise: getattr Exception if not found
    """

    if "." in plugin:
        package, plugin = plugin.rsplit('.', maxsplit=1)

    module = importlib.import_module(f".{plugin}_sql", package)
    model_type = model_type.replace('SQL', '')
    repository = getattr(
        module,
        f"{prefix or ''}{model_type}{SQL_REPOSITORY_POSTFIX}"
    )

    return repository


class APIModelSQL(APIModel):
    """ Override APIModel for MSSQL """

    pid: Optional[int] = Field(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'pid' in kwargs:
            setattr(self, 'pid', kwargs['pid'])

    if PYDANTIC_VERSION[0] == "2":
        model_config = ConfigDict(
            **(APIModel.model_config | dict(
                populate_by_name=True,
                arbitrary_types_allowed=True,
                json_encoders={datetime: str},
                extra="allow"
            ))
        )
    else:
        class Config(APIModel.Config):
            allow_population_by_field_name = True
            arbitrary_types_allowed = True
            json_encoders = {datetime: str}
            extra = "allow"
