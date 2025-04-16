from cryptography.fernet import Fernet
from django.conf import settings
import hashlib

fernet = Fernet(settings.FERNET_KEY)

class CryptoUtils:
    @staticmethod
    def encrypt(value) -> bytes:
        if isinstance(value, bytes):
            data_to_encrypt = value
        elif isinstance(value, str):
            data_to_encrypt = value.encode('utf-8')
        else:
            raise ValueError("Data must be a string or bytes")

        encrypted_data = fernet.encrypt(data_to_encrypt)
        return encrypted_data

    def decrypt(value):
        return fernet.decrypt(value)

    def hash(value) -> bytes:
        return hashlib.sha256(value.encode()).hexdigest()