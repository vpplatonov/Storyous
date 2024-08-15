import importlib
from datetime import datetime
from typing import Optional

from fastapi_utils.api_model import APIModel, PYDANTIC_VERSION
from pydantic import Field, ConfigDict

COUNT_FIELD = "count"
NUM_UPDATE_FIELD = "num_rows"
DB_PRIMARY_KEY = "pid"
SCHEMA_BY_ALIAS = False
SQL_REPOSITORY_POSTFIX = "RepositorySQL"
DB_PLUGIN_PATH_ADD = "repos"
DEFAULT_DB_NAME_SPACE = 'storyous'


def get_repository_for_model(
        model_type: str,
        prefix: str = '',
        plugin='merchants',
        package='storyapi.db'  # Class.__module__.rsplit('.', maxsplit=1)[0]
):
    """ Get Repository Module name (plugin) by class __name__ & __module__

    :parameter: model_type: Class.__name__
    :parameter::plugin: Class.__module__.rsplit('.', maxsplit=1)[1]
    :parameter::package: Class.__module__.rsplit('.', maxsplit=1)[0]
    :raise: getattr Exception if not found
    """

    if "." in plugin:
        package, plugin = plugin.rsplit('.', maxsplit=1)

    if DB_PLUGIN_PATH_ADD:
        package = f"{package}.{DB_PLUGIN_PATH_ADD}"

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
        if DB_PRIMARY_KEY in kwargs:
            setattr(self, DB_PRIMARY_KEY, kwargs[DB_PRIMARY_KEY])

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
