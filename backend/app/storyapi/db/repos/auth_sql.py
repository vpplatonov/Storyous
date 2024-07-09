from common.db.mssql import RepositoryMSSQL
from common.services.cypher import Cypher
from storyapi.db.auth import AuthSQL


class ClientsAndAuthRepositorySQL(RepositoryMSSQL[AuthSQL]):
    primary_key = "client_id"
    pk_remove_on_create = False
    encrypt_secret = False

    def insert_update(self, data: AuthSQL):
        if self.encrypt_secret and (secret := getattr(data, 'secret', None)) is not None:
            data.secret = Cypher().encrypt(secret)

        return super().insert_update(data)
