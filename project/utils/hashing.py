import hashlib
import os

def hash_password(password: str, salt: str | None = None) -> str:
    if salt is None:
        salt = os.urandom(16).hex()
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${h}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _hash = stored.split("$", 1)
    except ValueError:
        return False
    return hash_password(password, salt) == stored
