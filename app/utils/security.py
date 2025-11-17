# app/utils/security.py
import hashlib


def hash_file_contents(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

