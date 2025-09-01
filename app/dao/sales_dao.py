# app/dao/sales_dao.py
from __future__ import annotations
from datetime import date
from typing import Iterable, Optional, Tuple
from .connection import get_conn
from app.dao import item_dao

def create_sales_import(nombre: str, archivo_hash: str) -> Optional[int]:
    with get_conn() as con:
        cur = con.cursor()
        try:
            cur.execute(
                "INSERT INTO sales_imports (nombre, archivo_hash) VALUES (?, ?)",
                (nombre, archivo_hash)
            )
            return cur.lastrowid
        except Exception:
            return None  # hash duplicado

def delete_month(year: int, month: int, location_ids: Optional[Iterable[int]] = None):
    """
    Borra ventas del rango [primer día del mes, último día del mes] (inclusive).
    Si location_ids es None, borra para todas las sucursales.
    """
    from calendar import monthrange
    d1 = date(year, month, 1)
    d2 = date(year, month, monthrange(year, month)[1])
    where = "fecha BETWEEN ? AND ?"
    params = [d1.isoformat(), d2.isoformat()]
    if location_ids:
        ids = tuple(int(x) for x in location_ids)
        where += f" AND location_id IN ({','.join('?'*len(ids))})"
        params.extend(ids)
    with get_conn() as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM sales WHERE {where}", params)

def resolve_item_id(codigo: str, ean: Optional[str] = None) -> int:
    return item_dao.get_or_create(codigo or None, "", ean or None)

def bulk_insert_rows(import_id: int, rows: Iterable[Tuple[int,int,str,float]]):
    """
    rows: iterable de (location_id, item_id, fecha_iso, cantidad)
    """
    with get_conn() as con:
        cur = con.cursor()
        cur.executemany(
            "INSERT INTO sales (import_id, location_id, item_id, fecha, cantidad) VALUES (?, ?, ?, ?, ?)",
            ((import_id, loc, item, fecha, cant) for (loc, item, fecha, cant) in rows)
        )

def sum_sales_between(location_id: int, item_id: int, start_date_iso: str, end_date_iso: Optional[str] = None) -> float:
    with get_conn() as con:
        cur = con.cursor()
        if end_date_iso:
            cur.execute(
                "SELECT COALESCE(SUM(cantidad),0) FROM sales WHERE location_id=? AND item_id=? AND fecha BETWEEN ? AND ?",
                (location_id, item_id, start_date_iso, end_date_iso)
            )
        else:
            cur.execute(
                "SELECT COALESCE(SUM(cantidad),0) FROM sales WHERE location_id=? AND item_id=? AND fecha>=?",
                (location_id, item_id, start_date_iso)
            )
        (s,) = cur.fetchone()
        return float(s or 0.0)
