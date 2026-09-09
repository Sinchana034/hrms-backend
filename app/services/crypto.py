from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings


class EncryptionError(Exception):
    pass


@lru_cache
def _fernet() -> Fernet:
    settings = get_settings()
    if not settings.encryption_key:
        raise EncryptionError(
            "ENCRYPTION_KEY is not set. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(settings.encryption_key.encode())


def encrypt(plaintext: str) -> str:
    """
    Encrypts a secret (OAuth tokens, etc.) for storage (Section 6.2 / 14:
    'Credentials/tokens encrypted at rest, backend-only').
    """
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        raise EncryptionError("Failed to decrypt value — wrong key or corrupted data")
