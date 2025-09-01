# app/services/sales_service.py
from __future__ import annotations
import pandas as pd
from datetime import date
from calendar import monthrange
from typing import Optional, Dict, Any, Tuple, List, Iterable, DefaultDict
from collections import defaultdict

from app.dao import sales_dao, location_dao
from app.utils.normalize import canonicalize_columns
from app.utils.dates import to_date
from app.utils.hashing import md5_file

def _to_num(val) -> float:
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    # 2.999,00 -> 2999.00 ; 4,000 -> 4.0
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        return float(s)
    except Exception:
        import pandas as _pd
        return float(_pd.to_numeric([val], errors="coerce").fillna(0.0)[0])

def _months_in_df(df: pd.DataFrame, col_fecha: str) -> List[Tuple[int,int]]:
    meses = sorted({(d.year, d.month) for d in df[col_fecha] if pd.notna(d)})
    return meses

def _delete_by_months(meses: Iterable[Tuple[int,int]], loc_ids: Optional[Iterable[int]]):
    meses = list(meses)
    if not meses:
        return
    for (y, m) in meses:
        sales_dao.delete_month(y, m, loc_ids if loc_ids else None)

def _iter_rows_grouped(df: pd.DataFrame, col_suc: str, col_cod: str, col_fec: str, col_can: str):
    # Devuelve (loc_id, codigo, fecha_iso, cantidad_sum)
    grp = df.groupby([col_suc, col_cod, col_fec], as_index=False)[col_can].sum()
    for _, r in grp.iterrows():
        loc_txt = r[col_suc]
        if not str(loc_txt).isdigit():
            raise ValueError(f"Sucursal inválida '{loc_txt}'. Debe ser un ID numérico (ERP).")
        yield int(loc_txt), str(r[col_cod]).strip(), r[col_fec].isoformat(), float(r[col_can])

def import_sales_from_excel(
    path: str,
    import_name: Optional[str] = None,
    allow_multi_month: bool = False
) -> Dict[str, Any]:
    """
    Importa ventas desde un Excel:
      - Si allow_multi_month=False: exige que el archivo sea de 1 solo mes (delete+insert de ese mes).
      - Si allow_multi_month=True: acepta múltiples meses y hace delete+insert por cada mes detectado.
    Columnas mínimas (case/acentos tolerados):
      - Sucursal
      - Fecha
      - Código (o 'Código Artículo')
      - Cantidad
    """
    df = pd.read_excel(path, dtype=str)
    df.columns = canonicalize_columns(df.columns)

    col_suc = "sucursal"
    col_fec = "fecha"
    col_can = "cantidad"
    col_cod = "codigo articulo" if "codigo articulo" in df.columns else "codigo"

    for c in (col_suc, col_fec, col_can):
        if c not in df.columns:
            raise ValueError(f"Falta columna '{c}' en el Excel de ventas.")
    if col_cod not in df.columns:
        raise ValueError("Falta columna 'codigo' en el Excel de ventas.")

    # Parseo
    df[col_suc] = df[col_suc].fillna("").astype(str).str.strip()
    df[col_cod] = df[col_cod].fillna("").astype(str).str.strip()
    df[col_fec] = df[col_fec].map(to_date)
    df[col_can] = df[col_can].map(_to_num)

    # Filtrar válidos
    df = df[(df[col_suc] != "") & (df[col_cod] != "") & (df[col_fec].notnull()) & (df[col_can] > 0)].copy()

    # Detectar meses
    meses = _months_in_df(df, col_fec)
    if not meses:
        raise ValueError("No se detectaron fechas válidas en el archivo de ventas.")

    if not allow_multi_month and len(meses) > 1:
        raise ValueError(f"El archivo contiene múltiples meses: {meses}. Activá la opción 'Permitir múltiples meses' para importarlo.")

    # Crear import_id (anti-duplicados por hash del archivo)
    h = md5_file(path)
    import_id = sales_dao.create_sales_import(import_name or path, h)
    if import_id is None:
        return {"status": "skipped", "reason": "archivo ya importado (hash duplicado)", "rows": 0}

    # Ids de sucursal presentes
    suc_ids = sorted({int(s) for s in df[col_suc].unique() if str(s).isdigit()}) or None

    # Borrar por mes/meses
    _delete_by_months(meses, suc_ids)

    # Insertar filas (resuelve item_id por código y asegura sucursales por ID)
    rows = []
    for loc_id, codigo, fecha_iso, cant in _iter_rows_grouped(df, col_suc, col_cod, col_fec, col_can):
        location_dao.create_with_id(loc_id, f"Suc {loc_id}", "sucursal")
        item_id = sales_dao.resolve_item_id(codigo)
        rows.append((loc_id, item_id, fecha_iso, cant))

    sales_dao.bulk_insert_rows(import_id, rows)

    return {
        "status": "ok",
        "import_id": import_id,
        "rows": len(rows),
        "months": [{"year": y, "month": m} for (y, m) in meses]
    }
