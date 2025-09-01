# app/dao/movement_dao.py
from __future__ import annotations
from .connection import get_conn


def insert_movement(
    tipo: str,
    item_id: int,
    location_id: int,
    delta: float,
    lote: str | None,
    fecha_venc: str | None,
    origen: str,
) -> int:
    """
    Inserta un movimiento (import, ajuste, recepción).
    Guarda delta (positivo o negativo), ligado a item + sucursal.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO movements (tipo, item_id, location_id, delta, lote, fecha_venc, origen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (tipo, item_id, location_id, delta, lote, fecha_venc, origen),
        )
        return cur.lastrowid
