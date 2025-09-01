# app/dao/item_dao.py
from __future__ import annotations
from .connection import get_conn


def get_or_create(codigo: str | None, descripcion: str, ean: str | None) -> int:
    """
    Busca un item por (codigo, ean). Si no existe, lo inserta.
    Retorna el id del item.
    - codigo y ean se normalizan a string sin espacios; si vienen vacíos → None.
    - descripcion siempre se guarda aunque esté duplicada; lo importante es la clave.
    """
    codigo = (str(codigo).strip() if codigo not in (None, "", "nan") else None)
    ean = (str(ean).strip() if ean not in (None, "", "nan") else None)

    with get_conn() as conn:
        cur = conn.cursor()

        # Buscar
        cur.execute(
            "SELECT id FROM items WHERE codigo IS ? AND ean IS ?",
            (codigo, ean),
        )
        row = cur.fetchone()
        if row:
            return row["id"] if isinstance(row, dict) else row[0]

        # Crear
        cur.execute(
            "INSERT INTO items (codigo, descripcion, ean) VALUES (?, ?, ?)",
            (codigo, descripcion, ean),
        )
        return cur.lastrowid
