# app/dao/stock_dao.py
from __future__ import annotations
from typing import Iterable, Optional
from .connection import get_conn


def upsert_stock(item_id: int, location_id: int, lote: Optional[str], fecha_venc: Optional[str], delta: float) -> bool:
    if delta == 0:
        return True
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE stock
               SET cantidad = cantidad + ?
             WHERE item_id=? AND location_id=?
               AND IFNULL(lote,'') = IFNULL(?, '')
               AND IFNULL(fecha_venc,'') = IFNULL(?, '')
            """,
            (delta, item_id, location_id, lote, fecha_venc),
        )
        if cur.rowcount == 0:
            cur.execute(
                "INSERT INTO stock(item_id, location_id, lote, fecha_venc, cantidad) VALUES(?,?,?,?,?)",
                (item_id, location_id, lote, fecha_venc, delta),
            )
        return True


def list_expiries(location_id: Optional[int] = None, q: Optional[str] = None) -> Iterable[dict]:
    """
    Devuelve stock + datos del item + 'ultima_carga' (máx TS de movements coincidentes).
    Filtros:
      - location_id: sólo esa sucursal
      - q: texto a buscar en codigo, ean o descripcion (LIKE %q%)
    Columnas: id, codigo, descripcion, ean, location_id, lote, fecha_venc, cantidad, ultima_carga
    """
    sql = """
        SELECT
            s.id,
            i.codigo,
            i.descripcion,
            i.ean,
            s.location_id,
            s.lote,
            s.fecha_venc,
            s.cantidad,
            (
              SELECT MAX(m.ts)
                FROM movements m
               WHERE m.item_id = s.item_id
                 AND m.location_id = s.location_id
                 AND IFNULL(m.fecha_venc,'') = IFNULL(s.fecha_venc,'')
                 AND m.tipo IN ('import','recepcion')
            ) AS ultima_carga
        FROM stock s
        JOIN items i ON i.id = s.item_id
        WHERE s.cantidad <> 0
    """
    params = []
    if location_id is not None:
        sql += " AND s.location_id = ?"
        params.append(location_id)
    if q:
        sql += " AND (i.codigo LIKE ? OR i.ean LIKE ? OR i.descripcion LIKE ?)"
        like = f"%{q}%"
        params.extend([like, like, like])

    sql += " ORDER BY s.fecha_venc IS NULL, s.fecha_venc ASC"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        cols = [c[0] for c in cur.description]
        rows = cur.fetchall()
    return [dict(zip(cols, r)) for r in rows]
