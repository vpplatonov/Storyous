import struct
from typing import Optional, Union

import pymssql
import pyodbc
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential

from common.config.settings import settings

# QAT1 DB connection by default: do not work for local host
AZURE_ENTRA_CONNECTION = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server=tcp:{settings.mssql_server}.database.windows.net,1433;"
    f"Database={settings.mssql_db_name};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=300;"
)
# Only for local env with fully qualified (localhost) mssql_server name
AZURE_SQL_CONNECTION = (
    "Driver={ODBC Driver 18 for SQL Server};"
    f"Server=tcp:{settings.mssql_server},1433;"
    f"Database={settings.mssql_db_name};"
    f"Uid={settings.mssql_username};"
    f"Pwd={settings.mssql_password};"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=30;"
)
SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h


def get_azure_entra_token() -> bytes:
    """ Connect to Azure Entra default over MS ODBC python

    :param sami - system-assigned managed identity
    https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python#authenticate-with-a-system-assigned-managed-identity
    :raise CredentialUnavailableError
    """

    # for user assigned mi:
    if settings.az_managed_identity_client_id:
        credential = ManagedIdentityCredential(client_id=settings.az_managed_identity_client_id)
    elif settings.az_system_assigned_managed_identity:
        credential = ManagedIdentityCredential()
    else:
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)

    return token_struct


def get_odbc_connection(connection_string: Optional[str] = None):
    """ AZURE_SQL_CONNECTION - does not work for Uid & Pass """

    while True:
        try:
            if ((connection_string and "localhost" in connection_string) or
                    (not connection_string and settings.mssql_server in ["mssql", "localhost"])):
                with pyodbc.connect(
                    connection_string or AZURE_SQL_CONNECTION,
                    autocommit=False
                ) as conn:
                    yield conn
            else:
                token_struct = get_azure_entra_token()
                with pyodbc.connect(
                    connection_string or AZURE_ENTRA_CONNECTION,
                    attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct},
                    autocommit=False
                ) as conn:
                    yield conn
        except (pyodbc.OperationalError, pyodbc.Error) as e:
            print(str(e))
            pass


def get_mssql_connection(as_dict: bool = True, **kwargs):
    """ Does not yield using 'with' keyword """

    try:
        connection = pymssql.connect(
            server=settings.mssql_server,
            user=settings.mssql_username,
            password=settings.mssql_password,
            database=settings.mssql_db_name,
            as_dict=as_dict,
            **kwargs
        )
        yield connection
    except pymssql.Error:
        pass
    else:
        connection.close()


def get_connection() -> Union[pyodbc.Connection, pymssql.Connection]:
    """ using next() to return connection itself """

    return (
        next(get_odbc_connection())
        if settings.mssql_driver == 'pyodbc'
        else next(get_mssql_connection())
    )
