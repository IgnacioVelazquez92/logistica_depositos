# app/utils/hashing.py
import hashlib


def md5_file(path: str) -> str:
    """MD5 del archivo completo (para diagnóstico y anti-duplicados)."""
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)
    return md5.hexdigest()
