# app/services/import_service.py
from __future__ import annotations

import pandas as pd
from typing import Optional

from app.dao import (
    inventory_dao,
    item_dao,
    stock_dao,
    movement_dao,
    location_dao,
    responsible_dao,
)
from app.utils.normalize import canonicalize_columns
# e.g. mapea "Fecha de Creacion" -> "fecha de creacion"
from app.utils.dates import to_date
from app.utils.hashing import md5_file


VENC_REQ = [
    "ean",
    "codigo articulo",
    "descripcion",
    "unidades por bulto",
    "bultos",
    "cantidad",
    "fecha de vencimiento",
    "fecha de ingreso",
]

RESUMEN_REQ = [
    "inventario_id",
    "nombre",
    "observacion",
    "fecha de creacion",
    "fecha de exportacion",
    "total filas",
    "tipo",
]


def _to_num(val) -> float:
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    # tolera coma decimal argentina ("0,6557")
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        try:
            import pandas as _pd
            return float(_pd.to_numeric([val], errors="coerce").fillna(0.0)[0])
        except Exception:
            return 0.0


def importar_excel(
    path_excel: str,
    # Soporta ambas variantes: por *nombre* o por *id* (backward compatible)
    sucursal_nombre: Optional[str] = None,
    responsable_nombre: Optional[str] = None,
    sucursal_id: Optional[int] = None,
    responsable_id: Optional[int] = None,
) -> int:
    """
    Importa el Excel (hojas: 'resumen' y 'vencimientos').
    Valida duplicados por (nombre + fecha_creacion + fecha_exportacion).
    Inserta: inventories, inventory_rows, upsert a stock y registra movements.
    Devuelve el inventory_id creado.
    """

    # ---- Leer 'resumen'
    resumen_df = pd.read_excel(path_excel, sheet_name="resumen")
    resumen_df.columns = canonicalize_columns(resumen_df.columns)
    resumen = resumen_df.iloc[0].to_dict()

    for k in ("nombre", "fecha de creacion", "fecha de exportacion", "tipo", "total filas"):
        if k not in resumen:
            raise ValueError(f"Falta columna '{k}' en hoja 'resumen'.")

    nombre = str(resumen["nombre"]).strip()
    observacion = resumen.get("observacion")
    fecha_creacion = resumen["fecha de creacion"]
    fecha_exportacion = resumen["fecha de exportacion"]
    tipo = str(resumen["tipo"]).strip()
    try:
        total_filas = int(resumen["total filas"])
    except Exception:
        total_filas = None

    # ---- Duplicado
    if inventory_dao.find_duplicate(nombre, fecha_creacion, fecha_exportacion):
        raise ValueError(
            f"Este inventario ya fue cargado: '{nombre}' "
            f"({fecha_creacion} / {fecha_exportacion})."
        )

    archivo_hash = md5_file(path_excel)

    # ---- Resolver sucursal y responsable (por id o por nombre)
    if sucursal_id is None:
        sucursal_nombre = (sucursal_nombre or "Sucursal 1").strip()
        sucursal_id = location_dao.ensure_location(sucursal_nombre, "sucursal")
    if responsable_id is None:
        responsable_nombre = (responsable_nombre or "Sistema").strip()
        responsable_id = responsible_dao.ensure_responsible(
            responsable_nombre, "")

    # ---- Insertar inventario
    inv_id = inventory_dao.insert_inventory(
        nombre=nombre,
        observacion=observacion,
        fecha_creacion=fecha_creacion,
        fecha_exportacion=fecha_exportacion,
        tipo=tipo,
        total_filas=total_filas or 0,
        sucursal_id=sucursal_id,
        responsable_id=responsable_id,
        archivo_hash=archivo_hash,
    )

    # ---- Leer 'vencimientos'
    df = pd.read_excel(path_excel, sheet_name="vencimientos")
    df.columns = canonicalize_columns(df.columns)
    for col in VENC_REQ:
        if col not in df.columns:
            df[col] = None

    df["unidades por bulto"] = df["unidades por bulto"].map(_to_num)
    df["bultos"] = df["bultos"].map(_to_num)
    df["cantidad"] = df["cantidad"].map(_to_num)

    # ---- Recorrido por filas
    for _, row in df.iterrows():
        ean = (str(row["ean"]).strip() if pd.notna(row["ean"]) else "")
        codigo = (str(row["codigo articulo"]).strip()
                  if pd.notna(row["codigo articulo"]) else "")
        desc = (str(row["descripcion"]).strip()
                if pd.notna(row["descripcion"]) else "")

        upb = _to_num(row["unidades por bulto"])
        bultos = _to_num(row["bultos"])
        cantidad = _to_num(row["cantidad"])

        fecha_venc = to_date(row["fecha de vencimiento"])
        fecha_ing = row["fecha de ingreso"]

        item_id = item_dao.get_or_create(codigo or None, desc, ean or None)
        cantidad_total = (bultos * upb) + cantidad

        inventory_dao.insert_inventory_row(
            inventory_id=inv_id,
            item_id=item_id,
            upb=upb,
            bultos=bultos,
            cantidad=cantidad,
            cantidad_total=cantidad_total,
            fecha_venc=fecha_venc,
            fecha_ingreso=fecha_ing,
        )

        stock_dao.upsert_stock(
            item_id=item_id,
            location_id=sucursal_id,
            lote=None,
            fecha_venc=fecha_venc.isoformat() if fecha_venc else None,
            delta=cantidad_total,
        )

        movement_dao.insert_movement(
            tipo="import",
            item_id=item_id,
            location_id=sucursal_id,
            delta=cantidad_total,
            lote=None,
            fecha_venc=fecha_venc.isoformat() if fecha_venc else None,
            origen=f"import:{inv_id}",
        )

    return inv_id
