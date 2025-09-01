# app/services/expiry_service.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
import configparser
from pathlib import Path
from app.dao.stock_dao import list_expiries
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
            crit = cfg.getint("thresholds", "critico",
                              fallback=DEFAULT_CRITICO)
            prox = cfg.getint("thresholds", "proximo",
                              fallback=DEFAULT_PROXIMO)
    except Exception:
        pass
    if crit > prox:
        crit, prox = prox, crit
    return crit, prox


def get_expiries(location_id: Optional[int] = None, q: Optional[str] = None, include_expired: bool = True) -> List[Dict[str, Any]]:
    crit, prox = _load_thresholds()
    rows = list_expiries(location_id, q)
    out: List[Dict[str, Any]] = []
    for r in rows:
        fv_date = to_date(r["fecha_venc"])
        dl = days_left(fv_date)
        if dl is None:
            estado = "SIN_FECHA"
        elif dl <= crit:
            estado = "CRITICO"
        elif dl <= prox:
            estado = "PROXIMO"
        else:
            estado = "OK"

        # Filtrar vencidos si include_expired = False
        if not include_expired and dl is not None and dl < 0:
            continue

        out.append({
            "id": r["id"],
            "codigo": r["codigo"],
            "descripcion": r["descripcion"],
            "ean": r["ean"],
            "location_id": r["location_id"],
            "lote": r["lote"],
            "fecha_venc": fv_date.isoformat() if fv_date else "",
            "dias_restantes": dl if dl is not None else "",
            "cantidad": r["cantidad"],
            "estado": estado,
            "ultima_carga": (str(r.get("ultima_carga")) if r.get("ultima_carga") else ""),
        })
    return out
