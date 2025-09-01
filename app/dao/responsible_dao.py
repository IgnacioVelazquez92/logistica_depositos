# app/dao/responsible_dao.py
from __future__ import annotations
from .connection import get_conn


def ensure_responsible(nombre: str, contacto: str = "") -> int:
    """
    Se asegura de que el responsable exista.
    Si no existe, lo crea. Devuelve el id.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO responsibles(nombre, contacto) VALUES(?, ?)",
            (nombre, contacto),
        )
        cur.execute("SELECT id FROM responsibles WHERE nombre=?", (nombre,))
        row = cur.fetchone()
        return row["id"] if row else None


def list_responsibles():
    """Lista todos los responsables."""
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre FROM responsibles ORDER BY nombre")
        return cur.fetchall()
