from typing import TypeVar
from common.config.settings import settings, Settings

# from common.db import COUNT_FIELD, DEFAULT_DB_NAME_SPACE

T = TypeVar('T')


class DotDict(dict):
    """Dot notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
