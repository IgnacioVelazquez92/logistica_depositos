# app/dao/location_dao.py 
from __future__ import annotations
from .connection import get_conn

def ensure_location(nombre: str, tipo: str = "sucursal") -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO locations(nombre, tipo) VALUES(?, ?)", (nombre, tipo))
        cur.execute("SELECT id FROM locations WHERE nombre=?", (nombre,))
        row = cur.fetchone()
        return row["id"] if row else None

def create_with_id(loc_id: int, nombre: str, tipo: str = "sucursal") -> int:
    """
    Crea la sucursal con ID explícito (para que coincida con el ERP).
    No pisa si ya existe.
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO locations(id, nombre, tipo) VALUES(?, ?, ?)",
            (loc_id, nombre, tipo)
        )
        return loc_id

def get_by_id(loc_id: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, tipo FROM locations WHERE id=?", (loc_id,))
        return cur.fetchone()

def list_locations():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre FROM locations ORDER BY nombre")
        return cur.fetchall()

def _count_stock(location_id: int) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT COALESCE(SUM(ABS(cantidad)),0) FROM stock WHERE location_id=?", (location_id,))
        v = cur.fetchone()
        return int(v[0] if v else 0)

def _count_inventories(location_id: int) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM inventories WHERE sucursal_id=?", (location_id,))
        v = cur.fetchone()
        return int(v[0] if v else 0)

def delete_location(location_id: int) -> None:
    """
    Borra la sucursal solo si NO tiene stock ni inventarios asociados.
    Lanza ValueError si no se puede borrar.
    """
    if _count_stock(location_id) > 0:
        raise ValueError("No se puede borrar: la sucursal tiene stock asociado.")
    if _count_inventories(location_id) > 0:
        raise ValueError("No se puede borrar: la sucursal tiene inventarios cargados.")

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM locations WHERE id=?", (location_id,))
