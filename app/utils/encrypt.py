"""
Encrypt user password
"""
import base64
import hashlib
import os


def get_salt() -> bytes:
    """
    get salt(bytes) by random
    Returns:
        salt(bytes)
    """
    return os.urandom(64)


def transfter_salt_to_str(salt: bytes) -> str:
    """
    transfer salt(bytes) to str
    Returns:
         salt(str)
    """
    return base64.b64encode(salt).decode('utf-8')


def transfer_salt_str_to_bytes(salt: str) -> bytes:
    """
    transfer salt(str) to bytes
    Returns:
         salt(bytes)
    """
    return base64.b64decode(salt)


def get_hash(text: str, salt: bytes) -> str:
    """
    Hash the text
    Returns:
        text hash result
    """
    digest = hashlib.pbkdf2_hmac('sha256', text.encode(), salt, 10000)
    hex_hash = digest.hex()
    return hex_hash
