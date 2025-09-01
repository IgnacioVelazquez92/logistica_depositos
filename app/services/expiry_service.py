# app/services/expiry_service.py  (REEMPLAZAR COMPLETO POR ESTE)
from __future__ import annotations
from typing import List, Dict, Any, Optional
import configparser
from pathlib import Path
from datetime import date
from app.dao.stock_dao import list_expiries
from app.dao.sales_dao import sum_sales_between
from app.utils.dates import to_date, days_left

DEFAULT_CRITICO = 7
DEFAULT_PROXIMO = 30

def _load_thresholds() -> tuple[int, int]:
    crit, prox = DEFAULT_CRITICO, DEFAULT_PROXIMO
    try:
        ini = Path(__file__).resolve().parents[2] / "config" / "thresholds.ini"
        cfg = configparser.ConfigParser()
        if ini.exists():
            cfg.read(ini, encoding="utf-8")
            crit = cfg.getint("thresholds", "critico", fallback=DEFAULT_CRITICO)
            prox = cfg.getint("thresholds", "proximo", fallback=DEFAULT_PROXIMO)
    except Exception:
        pass
    if crit > prox:
        crit, prox = prox, crit
    return crit, prox

def get_expiries(location_id: Optional[int] = None, q: Optional[str] = None, include_expired: bool = True) -> List[Dict[str, Any]]:
    """
    Devuelve la vista de vencimientos por lote, con:
      - recepción (primera_carga),
      - ventas acumuladas desde recepción,
      - restante estimado (lote),
      - días restantes y estado (CRITICO/PROXIMO/OK/SIN_FECHA)
    Mantiene columnas previas para compatibilidad con la UI.
    """
    crit, prox = _load_thresholds()
    rows = list_expiries(location_id, q)
    out: List[Dict[str, Any]] = []
    today_iso = date.today().isoformat()

    for r in rows:
        fv_date = to_date(r["fecha_venc"])
        dl = days_left(fv_date)
        if dl is None:
            estado = "SIN_FECHA"
        elif dl < 0:
            estado = "CRITICO" if include_expired else None  # si no incluye vencidos, se filtrará más abajo
        elif dl <= crit:
            estado = "CRITICO"
        elif dl <= prox:
            estado = "PROXIMO"
        else:
            estado = "OK"

        # Filtrar vencidos si include_expired = False
        if not include_expired and dl is not None and dl < 0:
            continue
        if estado is None:
            continue

        # Recepción (primera_carga) y total ingresado del lote
        primera = r.get("primera_carga")
        primera_iso = str(primera) if primera else ""
        ingresado = float(r.get("ingresado_total") or 0.0)

        # Ventas acumuladas desde recepción (si hay fecha de recepción)
        ventas_desde = 0.0
        if primera_iso:
            ventas_desde = sum_sales_between(
                location_id=r["location_id"],
                item_id=r["item_id"],
                start_date_iso=primera_iso[:10],  # fecha (día) de la primera carga
                end_date_iso=today_iso
            )

        restante_estimado = max(0.0, round(ingresado - ventas_desde, 3))

        out.append({
            "id": r["id"],
            "item_id": r["item_id"],
            "codigo": r["codigo"],
            "descripcion": r["descripcion"],
            "ean": r["ean"],
            "location_id": r["location_id"],
            "lote": r["lote"],
            "fecha_venc": fv_date.isoformat() if fv_date else "",
            "dias_restantes": dl if dl is not None else "",
            "cantidad": r["cantidad"],                 # stock actual (tabla stock)
            "estado": estado,
            "ultima_carga": (str(r.get("ultima_carga")) if r.get("ultima_carga") else ""),
            # Nuevas columnas
            "recepcion": primera_iso,
            "ingresado_lote": round(ingresado, 3),
            "ventas_desde_recepcion": round(float(ventas_desde), 3),
            "restante_estimado": restante_estimado,
        })
    return out
