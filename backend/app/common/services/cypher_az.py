import base64

from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm

from common.config.settings import settings


class CypherAzure:
    """ python API to Azure KeyVault """

    def __init__(self):
        credential = DefaultAzureCredential()
        key_client = KeyClient(
            vault_url=f"https://{settings.az_key_vault_name}.vault.azure.net/",
            credential=credential
        )

        key = key_client.get_key(settings.az_key_vault_key_name)
        self.crypto_client = CryptographyClient(key, credential=credential)

    def encrypt(self, text: str) -> bytes:
        """ convert to byte str """
        encryption_result = self.crypto_client.encrypt(
            EncryptionAlgorithm.rsa_oaep,
            plaintext=bytes(text, "utf-8")
        )

        return base64.b64encode(encryption_result.ciphertext)

    def decrypt(self, cypher_text: bytes) -> str:
        return self.crypto_client.decrypt(
            EncryptionAlgorithm.rsa_oaep,
            ciphertext=base64.b64decode(cypher_text)
        ).plaintext.decode()
