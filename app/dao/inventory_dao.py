# app/dao/inventory_dao.py
from __future__ import annotations
from .connection import get_conn


def insert_inventory(
    nombre: str,
    observacion: str | None,
    fecha_creacion,
    fecha_exportacion,
    tipo: str,
    total_filas: int,
    sucursal_id: int,
    responsable_id: int,
    archivo_hash: str,
) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO inventories
            (nombre, observacion, fecha_creacion, fecha_exportacion, tipo,
             total_filas, sucursal_id, responsable_id, archivo_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                nombre,
                observacion,
                fecha_creacion,
                fecha_exportacion,
                tipo,
                total_filas,
                sucursal_id,
                responsable_id,
                archivo_hash,
            ),
        )
        return cur.lastrowid


def find_duplicate(nombre: str, fecha_creacion, fecha_exportacion):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id FROM inventories
            WHERE nombre=? AND fecha_creacion=? AND fecha_exportacion=?
            """,
            (nombre, fecha_creacion, fecha_exportacion),
        )
        return cur.fetchone()


def insert_inventory_row(
    inventory_id: int,
    item_id: int,
    upb: float,
    bultos: float,
    cantidad: float,
    cantidad_total: float,
    fecha_venc,
    fecha_ingreso,
) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO inventory_rows
            (inventory_id, item_id, unidades_por_bulto, bultos, cantidad, cantidad_total,
             fecha_vencimiento, fecha_ingreso)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (inventory_id, item_id, upb, bultos, cantidad,
             cantidad_total, fecha_venc, fecha_ingreso),
        )
        return cur.lastrowid


def list_recent_inventories(limit: int = 20):
    """
    Devuelve los últimos inventarios cargados (para poder 'ver lo que ya cargué').
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT i.id, i.nombre, i.fecha_creacion, i.fecha_exportacion, i.tipo,
                   i.total_filas, l.nombre AS sucursal, r.nombre AS responsable
              FROM inventories i
              LEFT JOIN locations l ON l.id = i.sucursal_id
              LEFT JOIN responsibles r ON r.id = i.responsable_id
             ORDER BY i.id DESC
             LIMIT ?
            """,
            (limit,),
        )
        return cur.fetchall()
