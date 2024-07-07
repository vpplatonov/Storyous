from typing import Optional, Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str

    mssql_server: Optional[str]
    mssql_username: Optional[str]
    mssql_db_name: Optional[str]
    mssql_password: Optional[str]  # MSSQL_SA_PASSWORD env var
    mssql_driver: str = 'pymssql'  # 'pymssql' | 'pyodbc' second options

    az_managed_identity_client_id: Optional[str] = None
    az_system_assigned_managed_identity: Optional[Any] = None


settings = Settings()
