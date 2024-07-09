from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str

    # MSSQL
    mssql_server: str | None = None
    mssql_username: str | None = None
    mssql_db_name: str | None = None
    mssql_password: str | None = None
    mssql_driver: str = 'pymssql'  # 'pymssql' | 'pyodbc' second options

    # Azure
    az_managed_identity_client_id: str | None = None
    az_system_assigned_managed_identity: str | None = None
    az_key_vault_name: str | None = None
    az_key_vault_key_name: str | None = None

    # AWS
    aws_kms_access_key_id: str | None = None
    aws_kms_secret_access_key: str | None = None
    aws_kms_region: str = 'us-east-1'


settings = Settings()
