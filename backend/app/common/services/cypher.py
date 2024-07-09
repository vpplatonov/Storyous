import base64

from common.config.settings import settings
if settings.az_key_vault_name:
    from common.services.cypher_az import CypherAzure

if settings.aws_kms_access_key_id:
    from common.services.cypher_aws import CypherAWS


class Cypher:
    """ All clients have same method: encrypt decrypt """

    def __init__(self):
        self.client = CypherDummy()
        if settings.py.aws_kms_key_id:
            self.client = CypherAWS()
        if settings.az_key_vault_name:
            self.client = CypherAzure()

    def encrypt(self, text: str) -> bytes:
        return self.client.encrypt(text=text)

    def decrypt(self, cypher_text: bytes) -> str:
        return self.client.decrypt(cypher_text)


class CypherDummy:
    @staticmethod
    def encrypt(text: str) -> bytes:
        return base64.b64encode(text.encode())

    @staticmethod
    def decrypt(cypher_text: bytes) -> str:
        return base64.b64decode(cypher_text).decode()
